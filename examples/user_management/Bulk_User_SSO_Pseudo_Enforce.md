# Five9 SSO Enforcer Script

This script is designed to pseudo-enforce Single Sign-On (SSO) compliance for user accounts in a Five9 domain. It processes users in bulk, applying changes to passwords and emails based on the criteria defined. You can also run the script in "safe mode" to simulate the updates without modifying any user data.

## Features

- Update users' passwords to a randomly generated value.
- Set temporary email addresses for users.
- Disable password change capabilities for selected users.
- Filter users based on specific usernames, patterns, and roles.
- Support for safe-mode (dry-run) simulations with a default .
- Generate CSV reports of modified and error users.

## Usage

The script supports several command-line arguments for flexible user management. Below is the usage guide for the script.

### Command-Line Arguments

| Argument                  | Description                                                                 |
| --------------------------| --------------------------------------------------------------------------- |
| `--username`               | Five9 username (required).                                                  |
| `--password`               | Five9 password. If not provided, the script will prompt for it securely.    |
| `--safe_mode`              | Perform a dry run without modifying the users (1 = True, 0 = False).        |
| `--exclude_blank_federationId` | Exclude users with blank `federationId` (1 = True, 0 = False).           |
| `--temp_email`             | Temporary email address to set during updates (default: `five9-password-reset@somecompany.com`). |
| `--log_level`              | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).            |
| `--simulated_delay`        | Simulated delay in seconds between requests (default: 0).                   |
| `--hostalias`              | Five9 host alias (default: `us`). Available options: `us`, `ca`, `eu`, `frk`, `in`. |
| `--target_user_csv`        | Path to a CSV file containing usernames to update.                          |
| `--exclude_usernames`      | Comma-separated list of specific usernames to exclude from updates.         |
| `--exclude_patterns`       | Comma-separated list of patterns (e.g., domains) to exclude.                |
| `--output_subdir`          | Subdirectory where output CSV files will be saved (default: `private`).     |

### Example Usage

1. **Basic Run with Safe Mode (Dry Run)**:
   ```bash
   python sso_enforce.py --username myFive9Username --safe_mode 1
   ```

2. **Update Specific Users from a CSV File**:
   ```bash
   python sso_enforce.py --username myFive9Username --password myFive9Password --target_user_csv users.csv --safe_mode 0
   ```

3. **Excluding Certain Usernames and Domains**:
   ```bash
   python sso_enforce.py --username myFive9Username --exclude_usernames user1,user2 --exclude_patterns "@company.com" --safe_mode 0
   ```

4. **Simulating Delay Between Updates**:
   ```bash
   python sso_enforce.py --username myFive9Username --safe_mode 1 --simulated_delay 2
   ```

5. **Run Without Safe Mode (Actual Updates)**:
   ```bash
   python sso_enforce.py --username myFive9Username --safe_mode 0
   ```

6.  **Specify input files and output locations**:
   ```bash
   py bulk_user_SSO_pseudo_enforce.py --username myFive9Username --target_user_csv private/mycompany/users_to_enforce_2024-10-15.csv --temp_email five9-password-reset@mycompany.com --exclude_usernames wfaapiuser@mycompany.com --exclude_patterns @mycompany.com --output_subdir private/mycompany --safe_mode 0
   ```
### Output

The script generates two CSV files in the specified output directory:

- **`modified_users.csv`**: Contains details of successfully updated users.
- **`error_users.csv`**: Contains details of users for whom updates failed.

These files are stored in the subdirectory specified by the `--output_subdir` argument (default: `private`).

### Logs

The script logs information based on the log level specified with `--log_level`. Available levels are:

- `DEBUG`: Detailed information for diagnosing issues.
- `INFO`: General updates on the script's progress.
- `WARNING`: Warnings that indicate potential issues.
- `ERROR`: Errors encountered during execution.
- `CRITICAL`: Severe errors that may cause the script to terminate.

### Security

If the `--password` argument is not provided, the script securely prompts for the password using `getpass()`.

## Notes

- The `Five9Client` object used in the script requires an external library (`five9`) that handles the interaction with the Five9 SOAP API. Make sure your environment has access to this module.

- The script's `safe_mode` is highly recommended for testing before performing actual updates.
