"""One representative-project order for the homepage, library and its structured list."""
FEATURED_PROJECT_IDS = ('P10', 'P36', 'P09', 'P04', 'P02', 'P05')


def prioritize_projects(projects):
    by_id = {project['id']: project for project in projects}
    return ([by_id[pid] for pid in FEATURED_PROJECT_IDS]
            + [project for project in projects if project['id'] not in FEATURED_PROJECT_IDS])
