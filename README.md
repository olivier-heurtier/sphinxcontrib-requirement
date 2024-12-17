# sphinxcontrib-requirement
Sphinx extension to manage requirements

import from csv
Export to csv

Configuration

Requirements

    id (ex: SYS-1)
    status (DRAFT, APPROVED, REJECTED)
    contract (C1, C2)
    version (1, 2, 3)

    priority (HIGH, MEDIUM, LOW)
    type (FUNC, NONFUNC, PROJECT, etc.)
    subtype (DATA, USECASE, ..., PERFORMANCE, ..., TRAINING, ...)

    source (DOC #n, WORKSHOP #n, ...)
    subsystem
    target_version
    status (DRAFT, APPROVED, DEPRECATED)


Links

    :link: name:id

Template for html and latex per type
