"""Provide user authentication."""
import bcrypt

from myapp.models.data_processing import get_user


def hash_password(password):
    """Return a hashed password as byte decoded string."""
    pw_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pw_bytes, salt)
    return hashed_password.decode("utf-8")


def authenticate_user(user_name, password):
    """Return True if user could be authenticated
    against credentials stored in the database."""
    user_obj = get_user(user_name)
    return bcrypt.checkpw(password.encode("utf-8"),
                          user_obj["password_hash"].encode("utf-8"))


def main():
    """Main function for testing when running the script under main."""


if __name__ == "__main__":
    main()
