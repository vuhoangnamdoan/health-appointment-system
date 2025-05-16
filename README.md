# Healthcare Appointment Booking System

## Git Workflow

This project follows the GitFlow branching model:

- `master`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: Individual feature branches (e.g., feature/user-authentication)

### Development Workflow:

1. Create a feature branch from `develop`: `git checkout -b feat/specific-task develop`
2. Work on feature branch and commit changes
3. Push feature branch to GitHub: `git push -u origin feature/your-feature-name`/`git push`
4. Create a pull request `develop` (check the branch merge into)
5. After review, merge the feature branch into `develop`

When ready for release, a release branch will be created from `develop` and eventually merged into both `master` and back into `develop`.

┌─────────────────────────────────────────────────┐
│                Kubernetes Cluster               │
│                                                 │
│  ┌──────────┐    ┌─────────┐    ┌─────────────┐ │
│  │ Frontend │    │ Backend │    │  Database   │ │
│  │ Service  │━━━━│ Service │━━━━│ StatefulSet │ │
│  │(React.js)│    │(Django) │    │(PostgreSQL) │ │
│  └──────────┘    └─────────┘    └─────────────┘ │
│                                                 │
│  ┌─────────────┐  ┌──────────┐  ┌───────────┐   │
│  │  Ingress    │  │ Secrets  │  │   HPA     │   │
│  │ Controller  │  │ Manager  │  │           │   │
│  └─────────────┘  └──────────┘  └───────────┘   │
└─────────────────────────────────────────────────┘