# Source Code

This folder contains the cleaned source tree for LAOS Analysis Software v1.0.

The source was prepared from the release backup by keeping the files needed for
the application and removing generated cache files, logs, output folders, and
temporary backup files.

To run from source:

```bash
pip install -r ../requirements.txt
python main.py
```

From the repository root, the equivalent command is:

```bash
python src/main.py
```

The packaged Windows release remains the recommended route for normal use. The
source tree is provided for transparency, review, and further development.
