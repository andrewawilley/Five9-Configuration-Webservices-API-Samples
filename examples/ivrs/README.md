# Skill Transfer Module Usage

This script extracts skill transfer modules from a Five9 XML response and outputs the data to a CSV file.


## Usage

```sh
python skill_transfer_module_usage.py --username <Five9 username> [--password <Five9 password>] [--hostalias <host alias>] [--output <output file>] [--verbose]
```

### Arguments

- `--username`: (Required) Five9 username.
- `--password`: (Optional) Five9 password. If not provided, you will be prompted to enter it.
- `--hostalias`: (Optional) Five9 host alias. Default is `us`. Options are `us`, `ca`, `eu`, `frk`, `in`.
- `--output`: (Optional) Output CSV file name. Default is `private/ivr_skill_transfer_modules.csv`.
- `--verbose`: (Optional) Enable verbose output.

### Example

```sh
python skill_transfer_module_usage.py --username myusername --password mypassword --hostalias us --output output.csv --verbose
```

## Output

The script generates a CSV file with the following columns:

- `IVR Script`: Name of the IVR script.
- `Skill Transfer Module Name`: Name of the skill transfer module.
- `Skill Target`: Name of the skill target.
- `Target Type`: Type of the skill target (skill or variable).
- `Skill Target Order`: Order of the skill target.

## Logging

The script logs the time taken to pull IVR scripts and the total runtime. If the `--verbose` flag is set, it also logs the extracted skill transfer modules in JSON format.
