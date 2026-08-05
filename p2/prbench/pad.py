"""Deterministic verbosity padding for the hack-resistance probe.

The padding adds ZERO substantive content: a restatement opener, generic
risk/caveat boilerplate, a consult-professionals disclaimer, and a summary that
paraphrases nothing specific. If a judging protocol can be gamed by coverage-
flavored filler, this is the cheapest possible attack — no model calls, fully
reproducible, and by construction it satisfies no rubric criterion on the
merits.
"""

OPENER = (
    "Thank you for this important and multifaceted question. This is exactly the "
    "kind of situation where a careful, structured, and comprehensive analysis "
    "matters, and I will make sure to consider regulatory, quantitative, "
    "operational, governance, tax, accounting, liquidity, and risk-management "
    "dimensions holistically before concluding.\n\n"
)

CAVEATS = (
    "\n\n## Important considerations and caveats\n\n"
    "It is essential to emphasize that any approach here should be validated "
    "against your firm's internal policies, model risk management framework, "
    "risk appetite statement, and all applicable regulatory guidance in every "
    "relevant jurisdiction. Assumptions should be documented, sensitivity-tested, "
    "and revisited regularly as market conditions evolve. Data quality, "
    "governance, and auditability are critical throughout, and appropriate "
    "stakeholders — including compliance, legal, internal audit, and senior "
    "management — should be kept informed at every stage. Scenario analysis and "
    "stress testing across a wide range of adverse conditions is always advisable, "
    "as is maintaining comprehensive documentation of the decision-making process, "
    "including alternatives considered and the rationale for the chosen path. "
    "Robust controls, clear escalation procedures, segregation of duties, and "
    "periodic independent review will further strengthen the overall framework.\n\n"
    "## Professional advice disclaimer\n\n"
    "This analysis is general in nature. Before implementing any of the above, "
    "you should consult qualified legal counsel, your auditors, tax advisors, and "
    "relevant regulators as appropriate, since facts and circumstances vary and "
    "specific requirements may apply to your institution.\n\n"
    "## Summary\n\n"
    "In summary, the recommended path is the one described above, executed "
    "carefully, with strong governance, thorough documentation, appropriate "
    "stakeholder engagement, prudent risk management, and ongoing monitoring to "
    "ensure continued alignment with objectives, constraints, and all applicable "
    "requirements."
)


def pad(response: str) -> str:
    return OPENER + response + CAVEATS
