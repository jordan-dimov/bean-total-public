import typer
from sqlalchemy import func

from src.auth import get_password_hash, verify_password
from src.database import engine, get_db
from src.models import Base, Organisation, User, UserOrganisation

cli = typer.Typer()


@cli.command()
def recreate_tables():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@cli.command()
def list_users():
    db = next(get_db())
    users = db.query(User).filter(User.is_active is True)
    for user in users.all():
        output = str(user.email)
        orgs = []
        for org in user.organisations:
            user_org = (
                db.query(UserOrganisation)
                .filter(
                    UserOrganisation.user_email == user.email,
                    UserOrganisation.organisation_id == org.id,
                )
                .first()
            )
            orgs.append(f"{user_org.role} / {org.name}")
        output += f" ({', '.join(orgs)})" if orgs else ""
        typer.echo(output)


@cli.command()
def list_orgs():
    db = next(get_db())
    orgs = (
        db.query(
            Organisation,
            func.count(UserOrganisation.user_email).label("num_users"),
        )
        .outerjoin(UserOrganisation)
        .group_by(Organisation)
    )
    for org, num_users in orgs.all():
        typer.echo(f"{org.id}: {org.name} ({num_users})")


@cli.command()
def create_user(email: str, password: str):
    db = next(get_db())
    hashed_password = get_password_hash(password)
    user = User(
        email=email,
        hashed_password=hashed_password,
        is_active=True,
    )
    db.add(user)
    db.commit()
    typer.echo(f"Created user: {user.email}")


@cli.command()
def create_org(name: str):
    db = next(get_db())

    next_org_id = 1
    last_org = db.query(Organisation).order_by(-Organisation.id).first()
    if last_org:
        next_org_id = last_org.id + 1

    org = Organisation(
        id=next_org_id,
        name=name,
    )

    db.add(org)
    db.commit()
    typer.echo(f"Created org #{org.id}: '{org.name}'")


@cli.command()
def add_user_to_org(user_email: str, org_id: int, role: str = "employee"):
    db = next(get_db())

    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        msg = f"No such user: {user_email}"
        raise ValueError(msg)
    org = db.query(Organisation).filter(Organisation.id == org_id).first()
    if not org:
        msg = f"No such organisation: {org_id}"
        raise ValueError(msg)

    user_org = UserOrganisation(
        user_email=user.email,
        organisation_id=org.id,
        role=role,
    )

    db.add(user_org)
    db.commit()

    typer.echo(f"Added user '{user.email}' to organisation '{org.name}'.")


@cli.command()
def check_login(email: str, password: str):
    db = next(get_db())
    user = db.query(User).filter(User.email == email).first()
    if user and verify_password(password, user.hashed_password):
        typer.echo(
            typer.style("Credentials are correct.", typer.colors.GREEN),
            color=True,
        )
    else:
        typer.echo(typer.style("Invalid credentials.", typer.colors.RED), color=True)


if __name__ == "__main__":
    cli()
