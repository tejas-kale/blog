---
title: "Inside OpenAI’s agentic software factory"
source: "https://newsletter.pragmaticengineer.com/p/openai-software-factory"
author:
  - "[[Gergely Orosz]]"
published: 2026-09-15
created: 2026-09-21
description: "A deepdive into how Codex has “taken over” OpenAI, how the frontier lab builds its agentic software factory, and the engineering challenges of one billion users. Details from inside OpenAI"
tags:
  - "clippings"
---

It’s rare to work with an unlimited token budget, but at OpenAI, that’s what all engineers, researchers, finance colleagues, and marketing folks do. Recently, I visited one of the world’s leading frontier labs to find out how OpenAI operates today – and for a glimpse at where software engineering might be headed as a profession.

Plenty has changed since I [visited](https://newsletter.pragmaticengineer.com/p/san-francisco-is-back) OpenAI’s headquarters last year. Within a year, Codex has gone from a “nice-to-have” tool to being the backbone of pretty much everything at the company.

To learn more, I talked with seven engineering leaders and engineers there: Venkat Venkataramani (VP of Engineering, Applied Infra), Sulman Choudhry (Head of Engineering, ChatGPT), Andrew Ambrosino (Lead, Desktop), Joe Gershenson (Lead, Core Agent team), Akshay Nathan (Engineering Lead, Productivity), Ahmed Ibrahim (Engineer, Codex) and Steve Coffey (Engineer, Responses API). *Thanks to all for taking part!*

Today, we cover:

- **Codex takes over at OpenAI.** In a matter of months, nearly all OpenAI’s non-engineers moved over to Codex and ChatGPT Work without a mandate from above for it.
- **Death of the IDE & pull requests.** IDE usage has been down since January when Codex usage started to surge. PRs and code reviews need to be rethought.
- **OpenAI’s agentic software factory.** OpenAI has built a “software factory” with several automated, agentic feedback loops: for example, Perf Factory monitors production and kicks off Codex agents to automatically fix performance issues.
- **How engineering tooling & practices are changing.** Hand-built internal tools are slowly being replaced by Codex, which is increasingly preferred for debugging over specialized tools. Harness efficiency is critical in software factories.
- **Engineering for a billion users: how OpenAI scales up its infra.** They buy first and take it in-house later. Also, geographic infra distribution, capacity planning tactics and challenges.
- **Making OpenAI’s API more reliable and performant**. CPUs are becoming a bottleneck, doing slower deployments on purpose, and solving load challenges.
- **How the software engineering job is changing.** Engineering specializations are disappearing, judgment and agency are more important, and it only takes one or two engineers for previously “impossible” rewrites and migrations to succeed.

*Before we start, a scheduling update: I’m in New York for the week, attending the LDX3 conference and visiting a few startups and tech companies in the city, so there will be no edition of The Pulse on Thursday. Normal service resumes next week!*

*The bottom of this article could be cut off in some email clients. [Read the full article uninterrupted, online.](https://newsletter.pragmaticengineer.com/p/openai-software-factory)*

[Read the full article online](https://newsletter.pragmaticengineer.com/p/openai-software-factory)

## 1. Codex takes over at OpenAI

The takeaway from my visit to the company’s headquarters which really sticks out is that Codex – and lately Codex *and* ChatGPT Work – have taken over *everything* there, starting in around January. Desktop lead, Andrew Ambrosino, told me:

> “The big theme of the past months has been that everything is now a coding agent. Whether the visible code is your output or not, agents write your artifacts.
>
> Think of it like this: your entire life is via software. You have these powerful tools (agents) in your computer, and the ability to loop and reason and write code is the ability to do everything.”

The token usage chart below shows this sudden adoption surge:

![](images/inside-openais-agentic-software-factory-0.png)

In a four-month period, non-engineering orgs like finance, recruitment, and legal went from ~0% usage of Codex to 90% usage. Now, almost all OpenAI employees use Codex and ChatGPT Work weekly. So, what happened?

OpenAI released the Codex app for Mac in February and for Windows in March, and ChatGPT Work (powered by the Codex harness) in July. Following that, non-engineers there moved all their workflows over to Codex and then to Work. *Caveat: OpenAI’s internal version of Codex is a lot more advanced than its external counterpart because it’s plugged into pretty much every OpenAI system* – *similar to how [Ramp’s Inspect AI agent](https://newsletter.pragmaticengineer.com/p/why-ramp-built-inspect) has been wired up.*

The fascinating part of this is that OpenAI got close to 40% adoption across non-engineering teams at a time when the Codex app was hostile to non-engineering users (hard to use). Between February and April, the Codex app still showed the code on-screen, but even so, non-technical colleagues outside of engineering *still* used it because it could do complex work like researching and creating a presentation, document, spreadsheet, or tasks that produce rich output. Today, those folks are very heavy users of it.

**Being able to work for longer on more complex things drove adoption.** OpenAI added the /goal setting to Codex, where you can set up a goal for the agent and it keeps working until it is complete. Between April and May, usage surged from 60% to 90%. Andrew believes improvement in the harness’s handling of long-running tasks was one cause of this:

> “The number one thing that is changing is that people are starting to use threads for much longer, and this longer usage has been a breakthrough. It’s surprising to see the sheer length of time that people spend on a thread – even days! They often set a goal and then have the model crank.
>
> Codex being good at longer-running tasks seems to cause people to do fewer things in parallel. This is because a long-running agent often spins off other agents to do other things, reducing the surface area that you, as a human, have to manage.”

**“Awareness overhang” is another cause of the rapid adoption, the Codex team believes.** As Akshay Nathan, Engineering Lead, Productivity team, told me:

> “For a long time, we had a ‘capability overhang’: the models were capable but the products didn’t fully bring that out. Now, we’re seeing an awareness gap. Some people have figured out they can use Codex to monitor Slack, update Airtable, or create onboarding materials. But many others still use it for one task and then discover more uses from teammates via word-of-mouth.
>
> But there’s still so much more, under the surface, that you can do with Codex.”

**Role-specific and team-specific plugins are created and distributed.** Another thing that sped up adoption is that each group started to distribute useful role-specific workflows as plugins. Andrew explained why it’s important to not just offer a generic coding agent:

> “If you build a product that can do anything, teams need a way to make it their own. You can’t just give everyone an empty box. Skills and plugins let teams adapt the agent to their work. Sometimes, we also need a new app capability, like a browser that the agent can use alongside those skills. But the same building blocks already cover a lot of different roles.”

**Subject matter experts are embedded in ChatGPT Work engineering teams.** The models have become “smarter” than developers in some domains, so devs cannot channel “taste” into the harness in those areas. So, people who are domain experts are onboarded onto engineering teams. This is one outcome of ChatGPT Work being used by so many non-engineering domains: experts embedded with engineering advise developers on things like what a good slide deck, spreadsheet, or business report looks like.

*Of course, domain experts being in engineering teams is a decades-old best practice for building quality products. It seems like this gets rediscovered in different contexts every few years!*

**OpenAI is fully dependent on Codex and Work.** This is so much the case that in the event of even a minor outage, internal messages from colleagues alert the Codex and Work teams at the same time as – or before – automated alerts.

Basically, work happens through Codex and Work, and pretty much *nothing* else. *From the outside, this dependence on a single shared harness is particularly eye-catching; two years ago, there were no AI agents, only advanced AI autocomplete!*

## 2. Death of the IDE & pull requests

Late last year, the Codex team was torn about whether to release the Codex desktop app. Andrew recalls the hesitation:

> “In December 2025, we weren’t entirely sure if we would release the Codex app. We had the Codex CLI as a terminal, and there are large, feature-rich IDEs out there. So, would there be space for a dev tool that is between a terminal and an IDE? In my head, there was this future where it would not work out, and be the kind of ‘misfit’ like the iPad was.
>
> A lot of people buy iPads and then never use them: they either use their smaller, more portable smartphone *(which could be the equivalent of the CLI in this metaphor)*, or their feature-rich laptop *(the equivalent of the IDE).*
>
> Also, don’t forget that in November, Antigravity came out as a VS Code fork. This added to the feeling that perhaps we should have also forked VS Code for the Codex app. But still, we dismissed the temptation and went with our gut feeling that as AI agents get better, IDEs will matter less.”

Indeed, since January, IDE usage has gone down and OpenAI’s bet looks like a good one. However, the Codex app is becoming a *little* more akin to an IDE: for example, the ability to edit files inside the app was shipped in June.

**CI/CD systems are seeing massive load increases.** One sign of productivity gains from Codex is the amount of additional code flowing through OpenAI’s dev infra systems. More code being created and pushed leads to new scaling challenges which the team is currently heads-down on solving. Venkat Venkataramani, VP of Engineering, Applied Infra, said:

> “The number of pull requests (PRs) per engineer is growing like a hockey stick *(at a very high, accelerating rate)*. Every part of the build-test-deploy pipeline is seeing dramatically more load.
>
> We’re talking about roughly a 10x increase in load on some systems. At most companies, that kind of growth might happen over two or three years. At OpenAI, we see it in about six months.
>
> That level of acceleration exposes bottlenecks everywhere: version control has to handle far more code being written and pushed, CI/CD systems have to scale with it, and production release processes have to absorb a much higher rate of change.
>
> **Every month, we wake up to a new set of infrastructure scaling challenges to solve.** Just when we think we’ve created enough capacity for the next phase of growth, the model unlocks another wave of capabilities, which creates a new set of bottlenecks somewhere else in the system.”

**In this context, PRs and code reviews are being rethought.** They have “core primitives” in software engineering, but this level of development acceleration is an opportunity to reimagine them. Again, from Venkat:

> “The question we ought to ask ourselves in the middle of all this development acceleration is how do we reimagine many things we took for granted. For example, how do we reimagine the CI (continuous integration) and CD (continuous deployment) process? What does observability mean in this world, and how should people interact with pull requests?
>
> If you ask me, the way we do code review today makes less and less sense, and the same is true for pull requests.
>
> We’re now seeing agentic code reviews that look at code changes through a series of different lenses. In the past, it would have been impractical for a cloud infrastructure engineer and a security engineer to review every single code change. With agents, that becomes possible.
>
> **We can rethink how code is deployed with agents, too.** We are building an agent that “handholds” a change all the way to production — whether it’s a code change or a change behind a feature flag. It observes the relevant monitoring graphs, but can also build its own dashboard to monitor important signals. More of our code changes are going to production with this kind of agent monitoring.”

**An increasingly painful bottleneck is in deploying native mobile apps.** When there are ten times more pull requests, it’s challenging to deploy on the backend or the web and more infrastructure is needed to do so. Then, after you rework a CI/CD system and make sure there’s enough capacity to run them, you’ll be deploying that many more PRs to production.

This arises in the shipping of updates to native iOS and Android apps because every app update needs to go through Apple’s and Google’s manual approval processes which take hours or days to complete.

Talking with Sulman Choudhry, Head of Engineering, ChatGPT, he explained how the app review bottleneck is affecting iteration speed. Sulman used to work at Facebook and remembers how the social media company sped up shipping mobile releases:

> “Back in the 2010s, Facebook had a pretty important breakthrough in how to ship native mobile code faster. App Store releases went from monthly to bi-weekly to weekly. At the same time, experimentation and feature flags let teams ship code before it was ready to launch, then turn features on remotely when they were.
>
> That model brought a lot more velocity to mobile.
>
> In the age of Codex, I think we’re hitting the next version of this problem. Code generation is getting dramatically faster, but getting that code into users’ hands on native mobile is not. For Codex in particular, where usage is heavily mobile-first, that gap is already becoming painful for us and users.
>
> I expect the pressure here to increase quickly. If software can be written in minutes, waiting days or weeks to get it onto a phone starts to look increasingly absurd.
>
> We should be aiming for a world where shipping code on native mobile is as fast as shipping on the web. Getting there will probably require some creative rethinking of what we ship, when we ship it, and what can be activated remotely. Today, we’re nowhere close.”

*There’s some irony in how shipping a native iOS or Android app has the exact same challenges today as in 2008, when the App Store was launched. In 18 years, not much has changed! Apple still does not officially allow apps to bypass the App Store review process to ship meaningful experience changes.*

## 3. OpenAI’s agentic software factory

The idea of a “software factory” is similar to a physical factory where robots and humans produce autos together. In the software context, it is AI agents and humans producing software. Some manufacturing sites are fully automated “dark factories” where illumination isn’t needed because there are no humans. Could the same fully automated process emerge in software engineering? At OpenAI today, there’s a “software factory” running and it’s all built around Codex.

Here’s how the “traditional” software development pipeline used to look, compared to what OpenAI’s agentic infra pipeline looks like today, as described by VP of Engineering, Applied Infra, Venkat Venkataramani:

![](images/inside-openais-agentic-software-factory-1.png)

The pipeline:

**1. A human builder defines the desired outcome.** A software engineer or product manager specifies the problem and desired outcome. Judgment, prioritization, and taste are becoming more important for this phase. Interestingly, Venkat told me that engineers at OpenAI are becoming more like product managers than traditional systems engineers.

**2. Codex gathers context.** OpenAI has moved all its documentation inside of the source code, which makes it easier for agents to understand more of the code. Codex also has access to:

- Git repositories and GitHub
- Slack and Notion
- Internal data sources: Databricks, Datadog, internal logs, etc
- Internal Codex skills – some of which are maintained by OpenAI’s Codex implementation itself!

Codex is so “plugged” into OpenAI that new engineers are directed to ask Codex *any* questions they have during onboarding because it has a surprising amount of context.

**3. Codex implements code changes.** This part is trivial enough: Codex gets to work and makes a series of code changes until it reaches its goal, and then verifies that the software works as it should.

**4. Build & test, then CI.** The agent builds the code, runs the tests, fixes the code when it breaks the test, and then creates a pull request. This pull request triggers the continuous integration (CI) server to run and execute a more thorough suite of linters and tests. The agent babysits the PR until it’s “green”, fixing any CI failures and automatically updating the PR.

**New: a “perf harness”:** the agent also uses a perf harness to send problematic PRs to the Synthetics A/B framework for evaluating performance implications. As mentioned above, the load upon CI systems has increased greatly in the past six months.

**5. Agentic code review.** Instead of using one generic AI code reviewer, OpenAI spins off multiple agents, each with a “domain specialist” configuration. Venkat told me they see this as equivalent to having a human domain expert from each relevant infrastructure team review every change.

*Note from Gergely: I was skeptical about the claim that an agent that’s told to be a cloud infra specialist would produce a different review from a generic agent. However, all Codex agents have full access to OpenAI’s code and docs, so this “cloud infra expert” agent likely has gathered a lot of context about cloud infra setup and best practices, meaning it should provide highly targeted feedback. The important thing is how these “domain specialist” agents are set up, the context they have access to, and how they focus only on their own domain to make best use of their limited context window.*

**Code changes are classified by risk.** High-risk changes can be sent through stricter processes; for example, they might invoke more AI code reviews, or mandate that a human reviews it after the AI agents finish. Low-risk changes follow an easier path; areas of the codebase can opt in to an agent that will auto-approve low risk PRs, removing human acceptance as a bottleneck and improving velocity.

A neat thing about risk assessment is that OpenAI can automate when additional compliance input is needed: either automated (via another agent) or human review. With the quantity of PRs being produced, it simply wouldn’t be possible for humans to review all code without assistance.

Just like with CI, the coding agent babysits the comments and updates the PR to fix issues surfaced.

**6. Agentic deploy.** After a human approves a change to go to production, it is assigned its own agent with an instruction that could be summarized as:

“Handhold this change until it is safely and fully rolled out into production.”

Agents handhold both the code changes and the changes behind feature flags. For example, in the case of a change behind the feature flag, the agent will:

- Read the codebase and figure out where the feature flag lives
- Understand what the change does
- Decide which signals indicate success and failure
- **Builds its own monitoring dashboard to use** – *this is a pretty impressive improvement and something that’s new to me*
- Watches relevant production signals and its dashboard(s)

OpenAI’s long term goal is to have something like a “per-change autonomous SRE” (site reliability engineer) in the form of an agent that can deploy pretty much autonomously.

**7. Observe production.** Tools which track the production system:

- Dashboards generated by the agent during previous steps
- OpenAI’s internal observability stack, including a bunch of custom tools that generate logs, metrics, trace & wide event data

One big change at OpenAI since my previous visit, pre-Codex, is that back then, engineers created dashboards to monitor services whereas now, agents do this at the granularity of per-change deployment.

**8. Production monitoring feeds back into development.** OpenAI’s “Perf Factory” uses agents to sift through alerts and dashboards, de-duplicate signals, identify real latency regressions, root-cause them and propose fixes. This helps catch performance issues introduced by ongoing code changes, extending the workflow beyond deployment into continuous improvement.

**9. Respond to outages.** Sevbot is OpenAI’s internal incident response agent; unsurprisingly, it’s also built on top of Codex. When an incident is detected, the bot “wakes up.” Here’s what it does:

- Collects context about the incident
- Determines possible mitigations (but never executes any)
- Answers devs’ questions (it’s part of the Slack channel)
- An engineer can tell it to apply a specific mitigation

OpenAI’s goal is to get to the point where Sevbot can take autonomous action when mitigating some outages. The dream is that no humans be woken up outside of their working hours during an outage because Sevbot can handle “routine” outages autonomously, with humans reviewing its actions when they return to work. But as of now, oncall duty is not a thing of the past at the company.

## 4. How engineering tooling & practices are changing

Unsurprisingly, Codex is changing how easy it is to build internal tools and having an impact on standard engineering practices like debugging. Here’s what I gathered from talking with folks at OpenAI.

### Observability: hand-built internal tools slowly replaced by Codex

In order to establish whether Codex is working well, the team collects several types of data from it:

- **Direct user feedback:** Codex has a ‘thumbs up / thumbs down’ button inside the tool to gather user feedback about whether things work as expected.
- **Telemetry**: the tool gathers details like how long a normal turn (AI agent response) takes. The team then maps out distributions, paying special attention to the p90, p95, and p99 values

**OpenAI’s version of Codex is connected** to Datadog, Databricks, logs, and other data sources. It can go through them, create aggregates and JOIN statements, and answer questions on how parts of the system behave.

**“Purpose-built” dashboards and internal tools are slowly being replaced by Codex and ChatGPT Work-generated ones.** This surprised me because I know how useful internal tools like purpose-built dashboards are at the team level, and how useful log explorers were, pre-AI, for monitoring systems. For example, I’ve been on teams with a set of Grafana dashboards linked inside the team wiki and during an outage, we opened this page. We’d also tweak the dashboards and add new ones: it was somewhat of an effort, but it greatly helped the team. Plus, we had a set of custom-built tools that helped with debugging, such as log viewers.

But those dashboards and internal tools took some effort to build, and today they are disappearing at OpenAI thanks to Codex, to the point that it’s not dashboards which devs distribute, but rather the skills to build them. Joe Gershenson is lead on the Core Agent team. He said:

> “When it comes to internal tools like internal pages or dashboards; increasingly, we’re just building a skill that sits inside Codex, and distributing the skill itself.”

People still use and generate dashboards, but they’re not the same “permanent” dashboards. The [Sites plugin](https://openai.com/academy/chatgpt-sites/) makes it trivial to generate a lightweight web app from Codex, so most devs just instruct Codex to build a dashboard – or Codex may do so itself – and share these lightweight dashboards when it’s helpful for collaboration.

### Debugging or dealing with an outage? Just ask Codex

Codex has become unexpectedly capable during outages and for debugging, Joe told me:

> “Everyone I know inside of OpenAI has had an “a-ha!” moment of realizing this. For me, the first time it happened I was in the middle of a SEV (outage), and trying to figure out what was happening. I typed the description of what was going on in Codex. It spun for a while, then came back with a hypothesis which it turned out was right! It’s insanely magical when it happens.”

Again, Codex having access to pretty much all of OpenAI’s internal systems like observability, logs and sanitized data means it can cover a lot of ground during investigations; probably more than most engineers could, and *definitely* faster than if you or I went through logs by hand.

### Harness efficiency critical in ‘software factories’

I talked with Joe Gershenson and Ahmed Ibrahim, a software engineer on Codex and one of the top-three contributors to the project, about Codex as a harness. They told me:

> “Over the past year, we’ve discovered just how *important* the harness is. Before, we didn’t really pay too much attention to efficiency: our approach was pretty much for each team to have its own Python harness and do whatever ad hoc stuff they needed with it.
>
> But then, we noticed that the harness can help users “feel” the full power of the model, if written the right way.
>
> We then discovered how important the small details become inside the harness. For example, take the concept of transporting data. Inside Codex, we have this concept of a “turn,” which refers to tool calls, sending a request, sampling, and similar operations. When we optimize each turn, we’re optimizing for the model to have fewer roundtrips, and for these roundtrips to be more efficient.”

“Harness efficiency” is an important focus for the Codex team, but what is it? As per Joe and Ahmed, it’s about three things:

- **Token usage:** A harness that uses fewer tokens to accomplish a task is more efficient
- **Task success ratio**: a harness that succeeds more often than another is de facto also more efficient.
- **Latency**: a harness where tasks complete faster is also more efficient.

Improving token efficiency happens in three areas:

- **Tools**: exposing better tools typically improves efficiency in terms of lower latency and fewer tokens
- **Context**: assembling context carefully helps Codex to reuse cached model computations (the KV cache) and work more efficiently. What’s included also shapes its behavior: loading many plugins or instructions into context can prompt the model to spend extra tokens and tools on exploring them. Selecting the context relevant to a task can reduce this overhead.
- **Model improvement:** researchers “return” efficient harness tactics and strategies to the model to make it smarter and use fewer tokens in the future

**Keeping the KV cache as warm as possible greatly improves the harness’s efficiency.** KV cache means caching both the input (K) and the learned vector [the output of the calculations] (V), and is an important component of LLM inference. KV caching exists because attention calculation is quadratic: but with KV cache in-place, only newly appended tokens need be calculated, resulting in lower GPU cost and lower latency. *We cover more about the KV Cache in our [ChatGPT deepdive](https://newsletter.pragmaticengineer.com/i/141865286/challenge-1-kv-cache-and-gpu-ram).*

## 5. Engineering for a billion users: how OpenAI scales up infra

### Things (probably) unique to a frontier lab

Some factors seem special to frontier labs:

- **Rapid growth with no sign of it stopping (yet).** Every part of OpenAI’s infra has seen a 10x load increase every 9-18 months (!!) for the last four years. For example, VP of Engineering, Applied Infra, Venkat Venkataramani, told me that at Meta, load increased by three orders of magnitude over time. In comparison, at OpenAI that rate of growth occurred in a much shorter period. In terms of infra load, OpenAI is growing much faster than hyperscalers did in the 2010s.
- **Anticipating what breaks next is the big infra challenge.** Fixing a problem too late leads to an outage; obviously something to be avoided. But time spent on fixing something which may or may not break in the future comes at the cost of fixing more pressing things in the here-and-now, like something that just broke or is about to.
- **The shape of OpenAI’s demand changes as usage grows.** In 2022-2023, the main usage of OpenAI was as a Q&A machine with ChatGPT, which then shifted to more reasoning requests in 2024-2025. This year, it’s changed again to agents *doing* things, which means persistent connections, more tokens, and heavier infra usage per user.
- **No clarity on what the work will be in the near future.** OpenAI remains truly research-led, which means it’s not possible to predict what engineers will work on in a year’s time. This uncertainty makes nimbleness mandatory; a research breakthrough can create a product category that nobody expected.

### Structural advantages

OpenAI has two big advantages for scaling up its infra:

- **Hyperscaler advantage:** no need to build out cloud infra from scratch because they build on top of existing infra like Azure, AWS and other hyperscalers.
- **Open source advantage:** much of the software OpenAI uses across its infrastructure is open source, enabling it to move fast right from the start.

Of course, these characteristics apply to any company founded after 2015, by when hyperscalers had matured. But it’s worth noting them as advantages compared to the past when companies had a harder time scaling up things like compute and networking.

Advantages specific to OpenAI:

- **Late decision-making:** the company does not invest deeply into an area until it’s clear there’s a product-market fit. Combined with rapid prototyping, it means OpenAI tries out many ideas cheaply and commits to fewer of them.
- **Late binding of GPU capacity:** GPU availability is a challenge across the industry. OpenAI places as many GPU orders as possible, but holds off on allocating compute until it’s installed and ready to go. This helps create more optimal decisions, and goes against practices at other places where an org places an order for ‘X’ compute capacity to come online in ‘Y’ months. OpenAI has built custom tooling to manage this “late binding,” and internally, teams understand they cannot rely on compute being available well in advance.
- **Scale helps deal with scale:** now that OpenAI is at 1B active users, adding ~100M additional users over a long weekend (about 1-2M per hour) is less of a challenge. Incremental spikes are also easier for the infra to absorb.

### Buy first, bring in-house later

The “buy versus build” question is a recurring theme everywhere. Inside OpenAI, the default approach on whether to buy a solution from a vendor or build in-house is to buy first when it’s an option. Once the vendor solution starts breaking, they consider building their own solution in house.

One example is the audio stack behind [ChatGPT Advanced Voice](https://help.openai.com/en/articles/20001274-chatgpt-voice), a realtime voice experience. OpenAI bought a solution from an audio vendor at first, building their initial version on top of it. Then, as the product took off, the company hired [Justin Uberti](https://www.linkedin.com/in/juberti/), author of the WebRTC standard, to build a new voice stack and brought the product in-house in six months.

### Geographic infra distribution

OpenAI has infrastructure deployed on every continent except Antarctica, split between dozens of regions. We’re talking the full stack of infra: not just GPUs, but also CPUs, and networking. The company is multi-cloud, using Azure, AWS, Oracle, CoreWeave, and Cerebras. On top of this, OpenAI is building its own data center as part of the ‘Stargate’ project. So, how do they route user requests region-wise? The team told me they decide based on two categories:

- **Latency sensitivity**: for instant answers and Voice workloads, they attempt to route to proximate locations to users. These are use cases where the user experience is magical when networking latency stays at 50-100ms. If a response takes longer, the magic wears off fast.
- **Long-running:** for workloads when responses take seconds or longer, they route based on infra availability. These requests can tolerate additional networking hops in return for having access to compute that can execute requests efficiently.

### Capacity planning

At many companies, capacity planning involves engineering orgs forecasting how much compute and storage they’ll need, which is then sent up to company-level, after which the infra org negotiates with cloud providers and orders dedicated hardware. I’ve been part of processes like this, which work at companies growing at a comfortable, predictable pace. But how does OpenAI do capacity planning with growth at the high rate it is? Here’s what they told me:

- **Custom demand forecasting + supply chain tracking software.** Three engineers from the Infra team have built custom tooling to collect demand signals to help forecast future demand, plus close-to-realtime supply chain tracking to follow progress from ordering GPUs to when a cluster goes online.
- **Forecast-error margins remain too high.** The team says that even with their custom stack and access to a wealth of future demand signals, forecasting errors are still too high for their liking. Capacity forecasting is one of the hardest unsolved problems.
- **Sudden takeoffs cannot be predicted.** OpenAI experiences unexpected demand takeoffs, such as surges in usage of an existing product, or for new products like [ChatGPT Images](https://newsletter.pragmaticengineer.com/p/chatgpt-images). The reverse also happens when the capacity to take on rapid growth is put in place, but no demand surge appears! *We’ve covered the engineering in [scaling up ChatGPT Images.](https://newsletter.pragmaticengineer.com/p/chatgpt-images)*
- **Core principle: no silent degradation of systems.** One thing OpenAI refuses to do is to quietly reduce model intelligence in order to free up compute and serve more users; the product is either up and working as expected, or it’s down. *This approach is markedly different to Anthropic’s, which has [revealed](https://www.anthropic.com/engineering/april-23-postmortem) it degraded model capability without telling customers, [likely in a bid to deal with](https://newsletter.pragmaticengineer.com/p/the-pulse-did-capacity-shortages) compute shortage.*

As a result, compute remains scarce. To make the best use of the current compute, allocation of it is made according to a list of priorities:

- **Priority #1: keep the site up.** Allocate the compute which keeps things running.
- **Priority #2: strategic bets.** Allocate compute for the most important bets, like Codex, image generation, and others.
- **Data-driven decisions**: for other allocation decisions, the team collects live data on things like GPU utilization efficiency and return-per-compute spend. They then allocate in a way to spend “compute tokens” in the best way possible.

## 6. Making OpenAI’s API more reliable & performant

OpenAI’s API is the layer sitting between users and their GPUs and comes with its own interesting engineering challenges. Steve Coffey builds OpenAI’s Responses API, and explained how the “token path” works there:

![](images/inside-openais-agentic-software-factory-2.png)

### CPU bottleneck

Most people assume the thing that slows down token generation in a product like ChatGPT/Codex is GPU availability. But actually, Steve told me it’s frequently tokenization itself; a CPU problem:

- **Tokenization is more than “just” splitting into words.** Tokenization means splitting pieces of text into “tokens.” Tokens are the model’s vocabulary pieces, and not necessarily words!
- **Performance is important.** The tokenizer needs to find effective ways to map a potentially massive piece of text onto the model’s vocabulary. A more trivial way to do this is via a regular expression. OpenAI goes further: Steve recounted that an engineer rewrote a complicated regular-expression heavy code into low-level code, and saw a 3x performance improvement.
- **Tokenization cost increases with context size (usually linearly).** This is because the CPU needs to process the input text. A five-times longer text takes 5x as long to tokenize: this is pretty straightforward!
- **Codex makes tokenizing much harder.** Take these two examples:A “normal” ChatGPT-style interaction: prompt → model → answerA Codex-style interaction can be: prompt → model → run command → read file → model → edit file → model → run tests → edit file →…

OpenAI is now seeing runs with 40+ tool calls and every call needs to be tokenized again! The context keeps growing.

- **Request validation is CPU intensive.** Validating the request and running safety checks can be a lot more time-consuming than tokenization: a long, 100K-token context could spend 2,300 milliseconds (2.3 seconds) on validation alone.

### Slower deployment on purpose

A deployment of new code to the complete API fleet can take up to two hours, and reliable deployment has always been a high priority, which is why incidents such as the [four-hour outage last year](https://status.openai.com/incidents/01JXCAW3K3JAE0EP56AEZ7CBG3/write-up) are important to learn and adapt from. Here’s what a deployment typically looks like:

- New version
- → Canary deployment
- → observe
- → Baseline deployment (Wave 1)
- → observe
- → Wave 2 deployment
- → observe
- → Wave 3 deployment
- → observe
- → 100% deployment

With this deployment strategy, a bad code change won’t take down all of OpenAI’s services because it will be caught in an earlier wave and the rollout be halted or reversed. However, rollout slows as the size of OpenAI’s CPU fleet grows.

### AI load makes scaling infrastructure harder

The combination of growing CPU load and an already deliberately slower deployment strategy makes it harder to scale up OpenAI’s infrastructure to handle the next 10x load increase. Visualizing the problems:

![](images/inside-openais-agentic-software-factory-3.png)

### Solving load challenges

So, how does OpenAI respond to these challenges? Steve revealed the three biggest projects the team is taking on, currently:

**Migrate from Python to Rust to reduce CPU load:** the API layer was originally written in Python because researchers already use Python, so it’s much faster to iterate with a shared programming language.

The work the API does is input/output bound, so Python’s single-threaded processing should not be a problem assuming Python is optimized, which it was. But then, the workloads changed from being prompts: contexts increased, validation was added, safety logic was added, and more. Python’s performance downsides added up, so the API team has started a Rust rewrite.

A mere two engineers are working on this Python-to-Rust migration, and are making very heavy use of Codex. So far, they’ve rewritten 300,000 lines of code to Rust with no disruption to the service. Astra has been a major accelerator of the rewrite’s pace. Engineers told me they see a 3x increase in lines migrated between July and August using GPT-5.6, and also in the period August to September using Astra. Around 90% of Codex’s traffic is served through the Rust path and the team estimates the full migration will be complete in a few months.

*Note from Gergely: it’s interesting to note that Anthropic came to the exact same conclusion, independently: their platform team is also [busy migrating its API from Python to Rust.](https://newsletter.pragmaticengineer.com/i/208848940/claude-platform)*

**Tokenize only the deltas with WebSockets.** The problem that agentic tool calling introduced was that the full context kept being re-tokenized at the API level, meaning that after each tool call which Codex made, the complete history had to be re-tokenized. For a tool chain with 40 tool calls, this meant re-tokenizing the growing context window 40 times, which means more CPU usage and greater latency. It also results in a quadratic latency degradation.

Instead, with WebSocket streaming the API now tokenizes the context window once, then it stores the tokenized values in-memory, and tokenizes just the *delta* that comes back from the tool calls. By making this change, the API saw median request latency drop 30% practically overnight. As a bonus, CPU usage also fell.

**Proactive capacity management for GPUs.** While CPU usage has become challenging, there’s also a problem with GPUs: it takes 15-20 minutes to add GPU capacity from when demand arises because GPUs are not stateless. For them to function, the model needs to be loaded onto them, and OpenAI’s models are so large that it takes that long to copy over the weights and initialize the model.

The OpenAI team is responding with capacity forecasting and “warming up” GPUs in advance: they load models onto GPUs in advance of demand. This type of capacity management has some similarities with spinning up a new machine – although adding a new pod to Kubernetes doesn’t involve 15 minutes of latency!

## 7. How the software engineering job is changing

I asked all seven people whom I talked to at OpenAI how the software engineering role is changing there in context of everything covered in this article. Some main themes emerged:

### Engineering specializations are disappearing

There are no more dedicated frontend or backend engineering roles, nor mobile engineer specialization. Sulman Choudhry, ChatGPT’s Head of Engineering, told me:

> “Although I always thought specialization in engineering would, one day, go away, it’s still surprising how quickly it has happened. Last year, teams were still looking for an Android or iOS engineer for specialized work. But no more. Today, if something needs to get done, you just need a builder.
>
> Codex allows any builder to think at the problem’s own abstraction level. If, as an engineer, I understand user problems and have an intuition of how to solve them, I can do it, regardless of specialization.”

### Infra teams no longer receive questions on the support channel

It’s interesting that while infra teams still have Slack channels for internal support, those channels are virtually silent because practically no one uses them for support. Instead, engineers just ask Codex how to do something and it looks up the documentation and builds it!

A by-product of this is that infra engineers have more bandwidth for other things and have taken on the work that infra product managers used to do: they now decide on priorities, scope work, and build it. On the infra team, every engineer is a sort of product manager / engineer hybrid.

### What matters to engineers

I asked VP of Engineering, Applied Infra, Venkat Venkataramani, and also the Head of Engineering ChatGPT, Sulman Choudhry, what sets the best engineers apart:

- **Judgment**: is an approach the right one, or is another more optimal? Should a feature be shipped or binned?
- **Prioritization:** what’s the next most important thing to work on and what is not worth doing, right now?
- **Agency**: the best engineers relentlessly come up with ideas and parallelize with agents as much as possible without being prompted.
- **Taste**: what does “great” actually look like? Engineers with good taste produce standout artifacts in functionality, architecture, design, etc.

### New engineering layer at the AI-agent level

A lot more engineering effort at OpenAI goes towards solving the problem of how to make the agent / agent loop more effective. This is a multi-strand issue containing questions like:

- Which tools to expose to the harness?
- Which new tools could the harness work more efficiently with?
- How to structure context?
- How to make requests faster?
- How to build a platform around it?
- What skills or plugins can be created to make people’s work (or the harness) more efficient?

This layer has not existed before, and this is how I’d visualize it:

![](images/inside-openais-agentic-software-factory-4.png)

It’s clear that AI agents are taking over the writing of code, and so – at least inside OpenAI – engineers’ job is increasingly to design the environment that agents operate in. *Note from Gergely: I’m unsure if this change will happen at all companies given OpenAI’s main product is the model and harness, and they are selling a tool to enable more efficient work. This means they inevitably spend a lot of time on making the product more efficient and better!*

### Artifacts are the new pull requests for non-devs

An interesting observation from Akshay Nathan, Engineering Lead for Productivity:

> “One learning we’ve had is how for non-developers, creating ‘artifacts’ is their equivalent of what us devs see as pull requests. By ‘artifacts’ I mean things like documents, slides, and spreadsheets. This is the thing they want to get to: they iterate on it and often share with others when they are done. There are a surprising number of similarities to the pull request flow!”

### Non-developers are problem-solving like devs

More from Akshay:

> **“I think everyone basically is becoming a developer, in a way.** Non-developers are now thinking about their problems from the angles of:
>
> - How do I build this solution for this?
> - How do I iterate on the solution?
> - How do I share my artifact generated with people and get feedback?
>
> The big difference I see is that non-developers are realizing they can build software solutions for their problems.”

### Just one or two people can make “impossible” rewrites & migrations succeed

Prior to Codex, the Python-to-Rust API migration mentioned above would have probably been a six-person job of slow progress. Today, this has transformed to only needing two people who make rapid progress and get it done in just a few months. Rewrites and migrations that would have needed large teams before now involve just a couple of engineers and lots of Codex agents. *This is not too dissimilar to how migrations and rewrites are done at Anthropic, like [the Bun migration.](https://newsletter.pragmaticengineer.com/i/208848940/2-twelve-month-project-done-in-11-days-bun-rewrite-to-rust)*

## Takeaways

*Thanks again to everyone at OpenAI who contributed to this article.* The pace of change there since the last time I visited surprised me, especially how rapidly Codex/ChatGPT Work has spread among non-engineers, who are now using AI to create “artifacts” like documents, spreadsheets, slides and websites.

**It’s OpenAI’s “agentic software factory” that I find most impressive.** It’s now possible to build agentic systems that act on CI errors and warnings to produce fixes and then re-run CI, and also take action on code review comments. Since AI agents can also do code review comments, they can iterate on pull requests and fix obvious issues before a human gets involved. OpenAI also has a “Perf Factory” service that monitors production and raises fixes to further improve the system!

These capabilities are new and clearly useful. I’ve seen glimpses of similar, less ambitious proto-software factories elsewhere, in the form of agents one-shotting bug fixes based on customer reports, and submitting them for review. But OpenAI’s setup is by far the most advanced.

**Agents “babysitting” deploys feels like a novel and useful deployment strategy.** Rolling out changes to large systems used to be done in responsible fashion via gradual rollouts by engineers. It’s notable that OpenAI has managed to build a system that is able to do this rollout autonomously, with an agent taking ownership of the rollout.

**Of course, it can’t be forgotten that at OpenAI, token budgets do not exist and that the company is in the business of selling tokens.** If asked, I would caution against blindly copying innovations there for no other reason than the potential cost! But at OpenAI, they’re sparing no expense to build ever more capable AI models, and so far, the strategy is paying off handsomely.

Considering how the price of tokens is falling for models that are *almost* as good as the very best ones, it’s possible to predict that per-token costs will continue to drop. If so, more companies will be able to afford to not worry so much about the cost of tokens, and to set up similar agentic loops like what OpenAI already has in place.

One thing looks certain: cutting-edge and “AI-native” companies are likely to build software in ways that are much closer to what OpenAI does today than to the more traditional software development lifecycle of the 2010s and early 2020s.
