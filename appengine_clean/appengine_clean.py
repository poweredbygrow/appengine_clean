#!/usr/bin/env python3
"""Delete old AppEngine versions."""

import argparse
import asyncio
import collections
import operator
import sys
from typing import Dict, List, Tuple


async def get_versions(project: str) -> Dict[str, List[Tuple[str, ...]]]:
    """
    Get dictionary of appengine versions from Google.

    Key is the service name, value is a line containing information about the version.
    """
    cmd = ["gcloud", "--project", project, "app", "versions", "list"]
    print("Calling command:", " ".join(cmd))
    process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE)
    stdout, _ = await process.communicate()

    output = stdout.decode().strip().split("\n")

    versions = collections.defaultdict(list)
    # Remove header line
    for line in output[1:]:
        line: Tuple[str, ...] = tuple(line.split())
        service = line[0]
        versions[service].append(line)

    return versions


async def delete_old_versions_multiple(
    projects: List[str], num_to_keep: int, fake=False
):
    await asyncio.wait(
        [
            delete_old_versions(project, num_to_keep=num_to_keep, fake=fake)
            for project in projects
        ]
    )


async def delete_old_versions(project: str, num_to_keep: int, fake=False):
    """
    Delete old AppEngine versions.

    project: the GCP project ID
    num_to_keep: the number of versions of each AppEngine service to keep
    fake: if True, perform a dry run
    """
    versions = await get_versions(project)

    versions_to_delete = {}

    # Determine which versions to delete for each service and also which ones to keep for
    # each service.
    versions_to_keep = set()
    for service, versions_for_service in versions.items():
        _versions_to_delete = set()

        # The item at index 3 is the date... sort by date ascending
        versions_for_service.sort(key=operator.itemgetter(3))

        # Take from 0 to num_to_keep from last place (therefore keeping the num_to_keep newest
        # versions)... and those are the ones we'll delete
        to_delete = versions_for_service[:-num_to_keep]
        to_keep = versions_for_service[-num_to_keep:]
        for version in to_delete:
            _versions_to_delete.add(version[1])
        for version in to_keep:
            versions_to_keep.add(version[1])

        versions_to_delete[service] = _versions_to_delete

    # If something should be kept for 1 service, it must be kept for all! So remove the kept
    # services from the delete lists for all services
    for service, versions in versions_to_delete.items():
        versions -= versions_to_keep
        versions_to_delete[service] = versions

    # Union together all the versions to delete
    total_to_delete = set()
    for service, versions in versions_to_delete.items():
        total_to_delete = total_to_delete | versions

    # Go ahead and delete
    if total_to_delete:
        cmd = [
            "gcloud",
            "--quiet",
            "--project",
            project,
            "app",
            "versions",
            "delete",
        ] + list(total_to_delete)
        print("Running:", " ".join(cmd))
        if fake:
            return
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE
        )
        await process.wait()


async def async_main():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "project",
        nargs="+",
        help="The Google Cloud Platform project to delete versions from",
    )
    parser.add_argument(
        "num_to_keep", type=int, help="The number of versions to keep for each service"
    )
    parser.add_argument(
        "--force", action="store_true", default=False, help="Actually delete versions"
    )
    parser.add_argument(
        "--dry-run", action="store_true", default=False, help="Perform a dry-run"
    )
    args = parser.parse_args()

    if args.force and args.dry_run:
        print("Can't specify --force and --dry-run")
        sys.exit(1)

    if not args.force and not args.dry_run:
        print("Must specify one of --force or --dry-run")
        sys.exit(1)

    if args.num_to_keep < 5:
        print(
            "You're keeping only",
            args.num_to_keep,
            "versions. Are you sure you know what you " "are doing? (y/n) ",
            end="",
        )
        response = input()
        if response != "y":
            sys.exit(1)

    await delete_old_versions_multiple(
        args.project, args.num_to_keep, fake=args.dry_run
    )


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_main())
    loop.close()


if __name__ == "__main__":
    main()
