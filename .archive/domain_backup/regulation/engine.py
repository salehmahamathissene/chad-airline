class RegulatoryEngine:
    def __init__(self, regulations):
        self._regulations = tuple(regulations)

    def evaluate(self, *, action, context, evaluated_at: int):
        applicable = [
            r for r in self._regulations
            if r.effective_from <= evaluated_at
            and r.applies_to(action=action, context=context)
        ]

        results = [
            r.evaluate(
                action=action,
                context=context,
                evaluated_at=evaluated_at
            )
            for r in applicable
        ]

        for result in results:
            if not result.allowed:
                return result

        return self._merge(results)

    def _merge(self, results):
        obligations = tuple(
            o for r in results for o in r.obligations
        )
        return ComplianceResult(
            allowed=True,
            obligations=obligations,
            prohibitions=(),
            regulation_id="MULTI",
            law_version="COMPOSITE",
            evaluated_at=results[0].evaluated_at if results else 0,
        )
