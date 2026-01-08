# Speckit Project Structure

This directory contains the project's constitutional governance framework and specification templates.

## Structure

```
.specify/
├── memory/
│   └── constitution.md          # Project constitution - immutable principles
├── templates/
│   ├── plan-template.md         # Technical planning template
│   ├── spec-template.md         # Feature specification template
│   ├── tasks-template.md        # Task breakdown template
│   └── commands/
│       └── constitution.md      # Constitution update command
└── README.md                    # This file
```

## Constitution (v1.0.0)

The constitution defines four core principles that govern all project decisions:

1. **Code Quality Excellence** - High standards for structure, documentation, and patterns
2. **Testing Standards & Reliability** - Comprehensive automated testing (80%+ coverage)
3. **User Experience Consistency** - Predictable, intuitive APIs and interfaces
4. **Performance Requirements** - Performance as a feature, not an afterthought

All features, specifications, and implementations MUST comply with these principles.

## Using Templates

### Planning a Feature

1. Copy `templates/plan-template.md` to your working directory
2. Fill in the constitution check section
3. Complete technical architecture and implementation details
4. Reference the plan in your specification

### Writing a Specification

1. Copy `templates/spec-template.md` to your working directory
2. Map each requirement to constitutional principles
3. Define acceptance criteria aligned with principles
4. Ensure non-functional requirements cover all four principles

### Breaking Down Tasks

1. Copy `templates/tasks-template.md` to your working directory
2. Categorize tasks by constitutional principle
3. Define clear dependencies and effort estimates
4. Track completion against Definition of Done

## Updating the Constitution

To propose changes to the constitution:

1. Use the `/speckit.constitution` command or manually edit `memory/constitution.md`
2. Follow semantic versioning for version bumps
3. Update all dependent templates to maintain consistency
4. Document changes in the Sync Impact Report
5. Obtain required approvals before merging

## Constitutional Compliance

Every code change should:
- Pass linting and type checking (Principle 1)
- Include tests with 80%+ coverage (Principle 2)
- Follow consistent API patterns (Principle 3)
- Meet performance targets (Principle 4)

## Questions?

Refer to `memory/constitution.md` for detailed requirements and rationale for each principle.
