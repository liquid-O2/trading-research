"""Failures that must remain visible in research and replay reports."""


class ContractError(ValueError):
    """An input violates a registered semantic or causal contract."""


class IntegrityError(ContractError):
    """Content, identity or evidence no longer matches its declaration."""


class DependencyUnavailable(ContractError):
    """A required observation, artifact or supported capability is absent."""

