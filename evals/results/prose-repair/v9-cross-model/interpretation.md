# What these comparisons support

On these three selected development cases, v9 is promising for Astra high, has no net head-to-head advantage over v4 on Sol low, and has a small favorable balance on Sonnet high. These are narrow diagnostics from one judge, not general model-family recommendations or fresh holdout results. The earlier broader evidence remains relevant.

## Argument writing

The two argument cases separate the models more clearly than the aggregate. Astra v9 wins once and ties once against no skill, and beats v4 twice. Sol v9 ties no skill twice and splits its comparisons with v4. Sonnet v9 beats no skill twice and splits its comparisons with v4.

In the museum recommendation, the judge prefers v4's purpose-first opening for Sonnet. In the reporting-policy argument, it likewise prefers v4's organization for Sol. Those losses matter: shortening the core did not uniformly improve paragraph progression.

Sonnet's reporting-policy win over v4 is a fidelity decision. V4 changes the source's statement that including raw readings *could* obscure exclusion decisions into an assertion that it *would*. The judge actually prefers v4's organization, but the frozen rubric prioritizes the stronger unsupported claim. This is a modest wording distinction, not a sweeping style improvement.

## Proofs

V9 beats no skill on the one proof for all three generators. Against v4, it wins on Astra and Sonnet and ties on Sol. All retain the correct variance formula. Manual inspection confirms that the new Sol and Sonnet proofs use conditioning to cancel the mixed term, preserve finite-population sampling, cover the degenerate cases, and never require independence.

Sonnet's two proof wins are driven by its saved baselines asserting that Y and Z are dependent. The source only says independence is not required. At N=2, Z is constant and hence independent of Y, so the added universal assertion fails within the stated scope. The judge flags this as minor: neither baseline's variance derivation is invalidated. V9 avoids the claim. The coordinator verified this counterexample, but that inspection is not an independent blind grade.

V9's Sonnet proof still puts one substantial centering identity inline. Its win should not be read as perfect compliance with the author's displayed-derivation preference. Proof references were unchanged; changing the core can still change proof exposition.

## Limits and practical reading

V9's 2W/0T/1L Sonnet balance over v4 comes from one organizational loss and two fidelity wins. V4 still has broader favorable Claude evidence, and this experiment covers Sonnet high only, not Opus or every effort level. Sol supplies no reason to prefer v9 to v4 overall on this set. The Astra result remains an encouraging development result rather than validation of a general repair.

Direct v4-versus-no-skill comparisons and Astra results were reused from source-verified saved grades. They were not inferred from v9 outcomes. Pairwise judgments across different batches need not form a transitive ranking; saved baselines and grades are also from earlier runs. There is no added order audit or replication. No skill or installation was changed, and both fresh holdouts remain sealed. The separate long-horizon test remains uncompleted.
