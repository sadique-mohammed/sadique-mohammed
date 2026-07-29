<div align="center">

<img src="./ascii.svg" width="460" alt="Mohammed Sadique"/>

<img src="./stats.svg" width="620" alt="Contributions in the last year"/>

[github.com/sadique-mohammed](https://github.com/sadique-mohammed) &nbsp;·&nbsp;
[linkedin](https://www.linkedin.com/in/mohammed-sadique20) &nbsp;·&nbsp;
[email](mailto:code.sadique@gmail.com)

</div>

<img src="./hd-about.svg" width="620" alt="about"/>

> Final-year CS student at GGSIPU, Delhi.<br>
> Backend and AI evaluation, mostly — I ship things and see if they hold up.

Most days that's <!-- TODO: link once the repo is public -->**RootCause AI**, a
Linux incident agent that only ever runs commands off a fixed allowlist. Before
that, a year evaluating and training coding models for Outlier AI / Shipd —
writing verifiers, ranking RLHF tasks, that kind of thing.

<img src="./hd-stack.svg" width="620" alt="stack"/>

<samp>python &nbsp; typescript &nbsp; javascript &nbsp; next.js &nbsp; react &nbsp; node &nbsp; postgres &nbsp; redis &nbsp; docker &nbsp; genai apis &nbsp; git &nbsp; linux</samp>

<img src="./hd-projects.svg" width="620" alt="projects"/>

<!-- TODO: swap each TODO-REPO-SLUG below for the real github.com/sadique-mohammed/<repo> path -->

**[RootCause AI](https://github.com/sadique-mohammed/TODO-REPO-SLUG)** &nbsp;·&nbsp; <samp>python, paramiko</samp><br>
Diagnoses Linux incidents — nginx failures, disk exhaustion, OOM — over SSH,
with every command checked against a hardcoded allowlist before it runs.

**[RizzInterviews](https://github.com/sadique-mohammed/TODO-REPO-SLUG)** &nbsp;·&nbsp; <samp>next.js, postgres, genai</samp><br>
Mock interview platform. Feeds a transcript through an adaptive difficulty
engine and gets back live DSA/web-dev questions with feedback, in real time.

**[Relay](https://github.com/sadique-mohammed/TODO-REPO-SLUG)** &nbsp;·&nbsp; <samp>typescript, postgres, genai</samp><br>
CLI agent for natural-language dev tasks — code generation, web search,
tool-calling — synced across devices over an OAuth device flow.

<img src="./hd-stats.svg" width="620" alt="stats"/>

<div align="center">

<img src="./streak.svg" width="620" alt="Current and longest streak"/>

<img src="./langs.svg" width="620" alt="Top languages by bytes and by repo"/>

<img src="./year.svg" width="620" alt="The last year, one character per day"/>

</div>

<img src="./hd-about-this-page.svg" width="620" alt="about this page"/>

Every graphic here is generated, not embedded from anyone else's server.
`ascii.svg` is a photo pushed through a character ramp by
[`scripts/make_portrait.py`](scripts/make_portrait.py); the stat graphics and
these section headings are drawn by [a scheduled action](.github/workflows/stats.yml)
straight from the GitHub GraphQL API, once a day, committing only what changed.

They animate with SMIL inside the SVG, because GitHub strips scripts from
READMEs — and since nothing loads from a third party, nothing here can
rate-limit or go dark. The headings are SVGs for the same reason: GitHub also
strips CSS, so an image is the only way to put this page's own typeface on them.

The typeface is [JetBrains Mono](scripts/fonts), subset to just the characters
each graphic draws and inlined as base64. That isn't only for looks: the
portrait's grid assumes an advance width of exactly 0.600 em, and a viewer whose
default monospace is narrower would otherwise see it squeezed.

Language totals cover public repositories only. `year.svg` uses the portrait's
character ramp: `:` `+` `#` `@`, quiet to loud.
