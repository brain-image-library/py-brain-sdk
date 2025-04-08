# bump_version.py
import re

def increment_version(version):
    # Split version into major, minor, patch
    major, minor, patch = map(int, version.split('.'))
    # Increment patch version by 1 (you can adjust to minor/major if needed)
    patch += 1
    return f"{major}.{minor}.{patch}"

def update_setup_py():
    # Read the current setup.py content
    with open("setup.py", "r") as f:
        content = f.read()

    # Find the current version using regex
    version_match = re.search(r'version="(\d+\.\d+\.\d+)"', content)
    if not version_match:
        raise ValueError("Version not found in setup.py")

    current_version = version_match.group(1)
    new_version = increment_version(current_version)

    # Replace the old version with the new one
    new_content = re.sub(
        r'version="\d+\.\d+\.\d+"',
        f'version="{new_version}"',
        content
    )

    # Write the updated content back to setup.py
    with open("setup.py", "w") as f:
        f.write(new_content)

    print(f"Updated version from {current_version} to {new_version}")

if __name__ == "__main__":
    update_setup_py()
