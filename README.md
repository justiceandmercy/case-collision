# case-collision

Detect file and directory names that collide on case-insensitive filesystems.

## Description

`case-collision` recursively scans a project and reports groups of paths that
differ only by case or Unicode normalization. These collisions can work on
Linux but break on macOS, Windows, or other case-insensitive filesystems.

## Features

- Recursively scans files and directories.
- Detects paths differing only by case.
- Detects paths differing only by Unicode normalization.
- Supports human-readable and JSON output.
- Returns a non-zero exit code with `--strict` for CI usage.
- Skips common dependency, build, and cache directories.

## Install

No external dependencies are required. Python 3.9 or newer is recommended.

```sh
git clone https://github.com/example/case-collision.git
cd case-collision
chmod +x case_collision.py
```

You can also copy `case_collision.py` into a project and run it directly.

## Usage

Scan the current directory:

```sh
python3 case_collision.py
```

Scan another project:

```sh
python3 case_collision.py /path/to/project
```

Emit JSON:

```sh
python3 case_collision.py --format json
```

Fail in CI when collisions exist:

```sh
python3 case_collision.py --strict
```

Example output:

```text
Case-insensitive path collisions:

group: readme.md
  README.md
  readme.md
```

## License

MIT
