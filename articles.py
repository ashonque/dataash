"""What the decision articles say. `build-articles.py` is the shape.

These are the pages for the searches that are really a choice somebody has
to make this week - not "what is a slowly changing dimension" but "type 1 or
type 2, for this dimension, now". Each opens with the answer, then earns it.
"""

ARTICLES = [

    # ------------------------------------------------------------------ 1
    {
        "slug": "scd-type-1-vs-type-2.html",
        "short": "SCD type 1 vs type 2",
        "oneline": "how to decide, one dimension at a time",
        "crumb": "SCD type 1 vs type 2",
        "title": "SCD type 1 vs type 2: how to decide, per dimension, and the mistakes that cost the most",
        "h1": "SCD type 1 or type 2? How to decide, one dimension at a time",
        "meta": "Type 1 overwrites; type 2 keeps history. The question that decides it, when each is "
                "right, what type 2 costs in rows and load logic, and the column you must never let it watch.",
        "tw": "One question decides it: must a report about the past keep saying what it said?",
        "keywords": "SCD type 1 vs type 2, slowly changing dimension, SCD type 2, SCD type 1, "
                    "ValidFrom ValidTo IsCurrent, dimension history, type 2 dimension load, "
                    "Kimball SCD, when to use SCD type 2",
        "standfirst": "The slowly changing dimension question is asked once per dimension, early, "
                      "and is expensive to change later. Here is the one test that answers it, "
                      "and the three ways it goes wrong.",

        "answer": [
            "Ask, for this dimension: <strong>if an attribute changes, must a report about the "
            "past keep saying what it said?</strong>",
            "If yes &mdash; a customer moved region and last year&rsquo;s sales must stay in the "
            "old region &mdash; that is <strong>type 2</strong>. If no &mdash; only the current "
            "value ever matters, and old values would be noise &mdash; that is "
            "<strong>type 1</strong>. Most warehouses have some of each, and the decision is per "
            "dimension, not per warehouse.",
        ],

        "sections": [
            {
                "id": "what", "h2": "What the two types actually do",
                "blocks": [
                    {"p": "A dimension row describes something &mdash; a customer, a product, a "
                          "store &mdash; and things change. The slowly changing dimension types are "
                          "the standard answers to what happens to the row when they do."},
                    {"h3": "Type 1: overwrite"},
                    {"p": "The old value is replaced and gone. One row per customer, always "
                          "showing the current state. Every fact that ever pointed at that customer "
                          "now reports under the new value, including facts from before the change."},
                    {"code": "DimCustomer  (type 1)\n"
                             "  CustomerKey   CustomerNumber   Region\n"
                             "  1001          C-4471           South     <- was 'North' until March; nobody can tell"},
                    {"h3": "Type 2: add a row"},
                    {"p": "The old row is closed and a new one opened. Several rows per customer, "
                          "each valid for a period. A fact points at whichever version was current "
                          "when it happened, so last year&rsquo;s sales stay in last year&rsquo;s "
                          "region."},
                    {"code": "DimCustomer  (type 2)\n"
                             "  CustomerKey  CustomerNumber  Region  ValidFrom   ValidTo     IsCurrent\n"
                             "  1001         C-4471          North   2019-01-01  2026-03-14  0\n"
                             "  2387         C-4471          South   2026-03-14  9999-12-31  1"},
                    {"p": "Note that the surrogate key changed and the business key did not. That "
                          "is the whole trick: the business key says <em>which customer</em>, the "
                          "surrogate key says <em>which version of them</em>. It is also why type 2 "
                          "is impossible without surrogate keys."},
                    {"h3": "Types 3 and 6, briefly"},
                    {"p": "Type 3 keeps a <code>PreviousRegion</code> column beside the current "
                          "one: exactly one step of history, for the case where a reorganisation "
                          "needs both views side by side for a while. Type 6 is a type 2 dimension "
                          "with a type 1 &ldquo;current value&rdquo; column added to every historical "
                          "row, so you can report by either. Both are real and both are far rarer "
                          "than the literature implies. Reach for them only when you can say which "
                          "question they answer that 1 and 2 cannot."},
                ],
            },
            {
                "id": "decide", "h2": "How to decide, attribute by attribute",
                "blocks": [
                    {"p": "The decision is made per dimension, but the evidence comes from its "
                          "attributes. Walk the columns and ask three things:"},
                    {"ol": [
                        "<strong>Does this attribute change at all?</strong> A date of birth does "
                        "not. A product&rsquo;s launch date does not. If nothing in the dimension "
                        "changes, the type 2 machinery is pure cost.",
                        "<strong>When it changes, does the past need the old value?</strong> "
                        "Region, segment, sales territory, price band, manager &mdash; almost always "
                        "yes, because reports are grouped by them and last year&rsquo;s numbers "
                        "must not move. Email address, phone number, a spelling correction to a "
                        "name &mdash; almost always no.",
                        "<strong>Is the attribute even the business&rsquo;s?</strong> "
                        "<code>ModifiedDate</code>, <code>RowVersion</code>, <code>LoadBatchID</code> "
                        "record that a system touched the row, not that anything about the customer "
                        "moved. See the third mistake below.",
                    ]},
                    {"p": "One volatile attribute whose history matters is enough to make the "
                          "dimension type 2. If none qualifies, type 1. If the volatile attribute is "
                          "one nobody groups by &mdash; a phone number &mdash; type 1 with a clear "
                          "conscience."},
                    {"note": "<strong>Flattened attributes count too.</strong> In a star schema, "
                             "<code>DimCustomer</code> often carries columns folded in from a parent "
                             "table &mdash; the territory name, the account manager. If the territory "
                             "is renamed and the customer dimension is type 1, that history is lost "
                             "just as surely as if the customer&rsquo;s own column had been "
                             "overwritten. A volatile inherited attribute argues for type 2 exactly "
                             "as much as a volatile local one. Netune&rsquo;s SCD advice judges the "
                             "folded-in columns alongside the table&rsquo;s own for this reason, and "
                             "names which one made the call."},
                ],
            },
            {
                "id": "cost", "h2": "What type 2 costs",
                "blocks": [
                    {"p": "Type 2 is the right default for anything people group by, and it is not "
                          "free. Know what you are buying."},
                    {"table": {
                        "head": ["", "Type 1", "Type 2"],
                        "rows": [
                            ["Rows", "One per thing", "One per version; grows with change rate"],
                            ["Load", "Update in place", "Close the old row, insert the new, compare "
                                     "to detect the change"],
                            ["Fact load", "Look up the key", "Look up the key <em>that was current "
                                          "on the fact&rsquo;s date</em>"],
                            ["Query", "Filter nothing", "Filter <code>IsCurrent = 1</code> for a "
                                      "&ldquo;now&rdquo; view, or join on date range for history"],
                            ["Correcting a typo", "Overwrite", "Also overwrite &mdash; a correction "
                                                  "is not a change; do not open a version for it"],
                            ["Undo later", "Cannot recover history", "Can collapse to type 1 any time"],
                        ],
                    }},
                    {"p": "That last row is the asymmetry that settles most arguments: a type 2 "
                          "dimension can always be read as type 1 (<code>WHERE IsCurrent = 1</code>), "
                          "but a type 1 dimension cannot be turned into type 2 after the fact, "
                          "because the history was never stored. When genuinely unsure, type 2 is "
                          "the reversible mistake."},
                ],
            },
            {
                "id": "mistakes", "h2": "The three expensive mistakes",
                "blocks": [
                    {"h3": "Making everything type 2 to be safe"},
                    {"p": "It feels cautious and it is not. A dimension with twelve attributes that "
                          "all open new versions gains rows for every trivial edit, the fact load "
                          "slows down resolving date-ranged keys, and analysts who forgot "
                          "<code>IsCurrent = 1</code> double-count everything. Type 2 the "
                          "dimensions whose history someone will actually ask for; type 1 the rest."},
                    {"h3": "Retrofitting type 2 after a year of type 1"},
                    {"p": "By then the history is gone. The dimension can be switched to type 2 "
                          "from today onward, but every fact before the switch points at a single "
                          "version that claims to have been true forever. Decide up front, which is "
                          "why the question belongs in the design and not in the second sprint."},
                    {"h3": "Letting the change test watch housekeeping columns"},
                    {"p": "This is the quiet one. If a type 2 dimension compares <em>every</em> "
                          "column to detect change, and the source carries a "
                          "<code>ModifiedDate</code> or a <code>rowversion</code>, then every batch "
                          "that touches the source row opens a new version of the customer. After "
                          "a year the dimension holds a detailed history of the source "
                          "system&rsquo;s maintenance schedule and almost nothing about the business "
                          "&mdash; and it is enormous."},
                    {"p": "The fix is to restrict the <em>change test</em> to the attributes that "
                          "describe the business, while still writing every column. Netune marks "
                          "those columns <code>tracked</code>, hashes only them when deciding "
                          "whether to open a version, and names the ones it ignored in a comment at "
                          "the top of the load procedure, so the decision is visible."},
                ],
            },
            {
                "id": "load", "h2": "What a type 2 load looks like",
                "blocks": [
                    {"p": "For anybody writing it by hand, the shape is always the same and every "
                          "step matters:"},
                    {"ol": [
                        "Stage the incoming rows.",
                        "For each incoming row, find the <strong>current</strong> version by "
                        "business key (<code>IsCurrent = 1</code>).",
                        "Compare the <strong>tracked</strong> attributes &mdash; a hash of them is "
                        "cheaper than a column-by-column comparison and is not fooled by column "
                        "order.",
                        "Where they differ: set the old row&rsquo;s <code>ValidTo</code> to now and "
                        "<code>IsCurrent</code> to 0, insert the new row with <code>ValidFrom</code> "
                        "now, <code>ValidTo</code> far future, <code>IsCurrent</code> 1.",
                        "Where the key is new: insert as a first version.",
                        "Where nothing tracked changed but an untracked column did: update in place "
                        "&mdash; that is the type 1 part of a type 2 dimension.",
                        "Keep the <code>-1</code> unknown row, so a fact whose customer cannot be "
                        "resolved lands somewhere and is still counted.",
                    ]},
                    {"p": "Which methodologies ask this question at all? "
                          "<a href=\"/kimball-dimensional-modeling.html\">Kimball</a> and "
                          "<a href=\"/galaxy-schema.html\">Galaxy</a>. "
                          "<a href=\"/data-vault-2-0.html\">Data Vault</a>, "
                          "<a href=\"/anchor-modeling.html\">Anchor</a> and "
                          "<a href=\"/inmon-corporate-information-factory.html\">Inmon&rsquo;s "
                          "core</a> keep every version by construction, so there is nothing to "
                          "decide; <a href=\"/one-big-table.html\">One Big Table</a> keeps none."},
                ],
            },
        ],

        "faq": [
            {"q": "Should I default to SCD type 2?",
             "a": "For any dimension people group reports by &mdash; region, segment, category, "
                  "territory &mdash; yes, because type 2 can always be read as type 1 later and the "
                  "reverse is impossible. For dimensions nobody groups by, or whose attributes never "
                  "change, type 1 is cheaper and honest."},
            {"q": "Can one dimension be type 1 for some columns and type 2 for others?",
             "a": "Yes, and most real type 2 dimensions are. Changes to tracked attributes open a "
                  "new version; changes to the others are overwritten in place. The dimension is "
                  "called type 2 because it can hold history, not because every column triggers it."},
            {"q": "Does a correction count as a change?",
             "a": "No. A typo fixed in a customer's name was never true, so there is no history to "
                  "keep &mdash; overwrite it. A type 2 version should mean the world changed, not "
                  "that somebody noticed a mistake."},
            {"q": "Why does type 2 need surrogate keys?",
             "a": "Because one customer now has several rows, so the business key is no longer "
                  "unique and cannot be the primary key or the target of a fact's foreign key. The "
                  "surrogate identifies the version; the business key identifies the customer."},
            {"q": "What is the difference between SCD type 2 and Data Vault's satellites?",
             "a": "Same idea, different place. A satellite is insert-only and keeps every version "
                  "automatically, so Data Vault has no per-dimension decision to make. Type 2 is the "
                  "dimensional model's way of opting a particular dimension into that behaviour."},
        ],

        "related": [
            ("kimball-dimensional-modeling.html", "Kimball dimensional modelling", "where the SCD question lives"),
            ("kimball-vs-data-vault.html", "Kimball vs Data Vault", "one keeps history by choice, the other by construction"),
        ],
        "cta_h": "See which of your dimensions argue for type 2",
        "cta_p": "Netune profiles the real data, works out which attributes change and whether "
                 "anything groups by them, and recommends a type per dimension with the reason "
                 "named &mdash; including the folded-in columns most people forget.",
    },

    # ------------------------------------------------------------------ 2
    {
        "slug": "what-is-a-staging-layer.html",
        "short": "What a staging layer is for",
        "oneline": "and the four things it must never do",
        "crumb": "Staging layer",
        "title": "What a staging layer is for in a data warehouse, and what it must never do",
        "h1": "What a staging layer is actually for (and the four things it must never do)",
        "meta": "Why every warehouse methodology has a staging layer, the three jobs it does, the "
                "four things that must not happen in it, and how it differs from a landing zone "
                "and from Medallion's bronze.",
        "tw": "Three jobs, four rules, and why it is a heap with no indexes.",
        "keywords": "staging layer data warehouse, staging area, staging tables, what is staging "
                    "in ETL, staging vs landing zone, staging vs bronze, truncate and load, "
                    "persistent staging, staging schema SQL Server",
        "standfirst": "Staging is the layer every methodology shares and nobody writes about, "
                      "which is why it is where the strangest decisions get made.",

        "answer": [
            "A staging table is <strong>a typed copy of one source table, and nothing else</strong>: "
            "no keys resolved, no history applied, no business rules, the source&rsquo;s own column "
            "names. It exists to keep the transformation off the production system, to give a "
            "failed load somewhere to restart from, and to be the one place the data still looks "
            "exactly like the source when a number turns out wrong.",
            "Yes, you need one, whichever methodology you choose. No, it is not where the "
            "modelling happens.",
        ],

        "sections": [
            {
                "id": "jobs", "h2": "The three jobs it does",
                "blocks": [
                    {"h3": "1. It protects the source system"},
                    {"p": "A warehouse load that reads directly from production holds locks, "
                          "competes for I/O, and turns a slow transformation into a slow "
                          "application. Staging reads the source once, as plainly as possible, and "
                          "everything downstream reads staging. The production system has one "
                          "cheap visitor per run rather than a dozen expensive ones."},
                    {"h3": "2. It gives a failed load somewhere to restart from"},
                    {"p": "Warehouse loads fail. A dimension lookup finds an unexpected NULL, a "
                          "type conversion trips on one row in ten million, somebody renamed a "
                          "column. Without staging, the fix means going back to the source and "
                          "extracting again &mdash; and the source has moved on since. With "
                          "staging, the extract is already done and the load restarts from the "
                          "step that failed."},
                    {"h3": "3. It is where you go when a number is wrong"},
                    {"p": "Somebody says the revenue figure is off. The warehouse has resolved "
                          "keys, applied history and summed things; the source system has been "
                          "updated three times since. Staging is the only place holding the data "
                          "as it was at the moment of the load, in the source&rsquo;s own shape, so "
                          "you can tell whether the warehouse mis-transformed it or the source sent "
                          "it that way. That single property pays for the whole layer."},
                ],
            },
            {
                "id": "rules", "h2": "The four things it must never do",
                "blocks": [
                    {"p": "Every one of these is tempting, because staging is where the data is "
                          "first in your hands and it feels efficient to tidy it on the way in. "
                          "Each one quietly destroys one of the three jobs above."},
                    {"h3": "It must not apply business rules"},
                    {"p": "The moment staging filters out cancelled orders, or maps status codes "
                          "to words, it stops being a copy of the source &mdash; and job 3 is gone. "
                          "When the number is wrong you can no longer tell whether the rule or the "
                          "source is to blame. Rules belong in the layer that is allowed to have "
                          "opinions."},
                    {"h3": "It must not resolve keys"},
                    {"p": "Looking up surrogate keys during staging means staging depends on the "
                          "warehouse being loaded first, which inverts the layer order and makes "
                          "the restart point useless. Staging carries the source&rsquo;s own keys; "
                          "the warehouse load resolves them."},
                    {"h3": "It must not rename columns"},
                    {"p": "A staging column called what the source called it is one that can be "
                          "traced back without a mapping document. Rename it there and every "
                          "investigation starts with a translation step. Give things readable "
                          "names in the warehouse, and keep the source&rsquo;s names in staging "
                          "where they are evidence."},
                    {"h3": "It must not carry indexes or keys"},
                    {"p": "This one is about performance rather than honesty, and it is counter-"
                          "intuitive. A staging table is cleared and refilled every run, in bulk. "
                          "On SQL Server, a heap with no indexes loaded with <code>TABLOCK</code> "
                          "under the simple or bulk-logged recovery model is minimally logged; add "
                          "a clustered index and every row goes through the transaction log. A "
                          "primary key on a staging table also makes it refuse the duplicate rows "
                          "the source legitimately sent, which is exactly the kind of thing you "
                          "wanted to catch downstream rather than lose."},
                ],
            },
            {
                "id": "types", "h2": "Types: keep them, with five exceptions",
                "blocks": [
                    {"p": "A staging column has the source column&rsquo;s type. That is most of "
                          "what &ldquo;typed copy&rdquo; means. There are a handful of types SQL "
                          "Server cannot create or compare as they stand, and those are converted "
                          "once, at the boundary, so nothing downstream ever meets them:"},
                    {"ul": [
                        "<code>hierarchyid</code>, <code>geography</code>, <code>geometry</code> "
                        "&mdash; CLR types; staged as text via <code>.ToString()</code>",
                        "<code>xml</code>, <code>sql_variant</code> &mdash; staged as text via an "
                        "explicit <code>CONVERT</code>",
                        "<code>timestamp</code> / <code>rowversion</code> &mdash; eight bytes, not a "
                        "date; staged as <code>BINARY(8)</code>",
                    ]},
                    {"p": "Everything else crosses unchanged. Widening a column in staging and not "
                          "in the warehouse is how a load fails on a value too long for its target, "
                          "so if a type must change, it changes the same way on both sides."},
                ],
            },
            {
                "id": "shape", "h2": "Truncate-and-reload, or persistent?",
                "blocks": [
                    {"p": "The classic staging table is emptied and refilled every run "
                          "(<code>TRUNCATE</code>, falling back to <code>DELETE</code> for an account "
                          "without <code>ALTER</code> rights, then a bulk insert). It holds the "
                          "current extract and nothing older. That is the right default: cheap, "
                          "simple, and enough for the three jobs."},
                    {"p": "A <strong>persistent staging area</strong> keeps every extract, usually "
                          "with a load date, so you can see what the source said on any past run. "
                          "That is genuinely useful for audit and for rebuilding history after a "
                          "modelling mistake &mdash; and it is also what "
                          "<a href=\"/medallion-architecture.html\">Medallion&rsquo;s bronze</a> and "
                          "<a href=\"/data-vault-2-0.html\">Data Vault&rsquo;s raw vault</a> are, "
                          "under other names. If you find yourself wanting persistent staging, you "
                          "are probably choosing one of those two."},
                    {"p": "Incremental staging &mdash; copying only rows newer than a high-water "
                          "mark &mdash; is a performance choice, not a change of shape. Two things "
                          "about it worth knowing: the watermark should be derived from the target "
                          "(<code>MAX(column)</code>) rather than stored in a bookkeeping table, "
                          "because a stored watermark and the real data drift apart the first time "
                          "a run half-fails; and a <em>created</em> column and a <em>modified</em> "
                          "column give opposite results &mdash; one misses every update, the other "
                          "appends updates beside the rows they replace."},
                ],
            },
            {
                "id": "vs", "h2": "Staging, landing zone, bronze: what is the difference?",
                "blocks": [
                    {"table": {
                        "head": ["", "Staging", "Landing zone", "Bronze"],
                        "rows": [
                            ["What it holds", "The tables the design needs, typed for the warehouse",
                             "The source&rsquo;s own tables, unchanged, every column",
                             "Everything as it arrived, plus ingest metadata"],
                            ["Lifetime", "Refilled each run", "Refilled or appended each run",
                             "Kept &mdash; it is the archive"],
                            ["Purpose", "Feed the warehouse load", "Get the data off production so "
                             "modelling can happen somewhere else",
                             "Prove what was received, hash and all"],
                            ["Modelled?", "No", "No", "No"],
                            ["Who reads it", "The warehouse load", "Profiling, exploration, then staging",
                             "Silver"],
                        ],
                    }},
                    {"p": "They overlap because they are answers to neighbouring problems. A "
                          "landing zone is what you build when the modelling has not happened yet "
                          "and you need the data somewhere safe to look at. Staging is what the "
                          "design needs once it exists. Bronze is staging that promised never to "
                          "forget."},
                ],
            },
            {
                "id": "where", "h2": "Where it lives, and one detail about the log",
                "blocks": [
                    {"p": "Staging is usually a schema (<code>stg</code>) in the warehouse database, "
                          "or a database of its own on the same server. On SQL Server the same "
                          "server matters: the staging load reads the source with a three-part name "
                          "(<code>[SourceDb].[dbo].[Orders]</code>), and that only resolves locally. "
                          "A source on another server means a landing copy first, or a linked "
                          "server, and both are decisions rather than defaults."},
                    {"p": "One small thing that saves an afternoon: put the load log &mdash; the "
                          "table every load procedure writes a row into &mdash; in the "
                          "<em>warehouse</em> schema, not staging&rsquo;s, even though the staging "
                          "procedures write to it too. One table then records a whole run. Split "
                          "it by layer and you have two audit trails that have to be joined to "
                          "answer &ldquo;did last night work&rdquo;."},
                ],
            },
        ],

        "faq": [
            {"q": "Do I need a staging layer if my source is small?",
             "a": "Almost always, yes. The three jobs &mdash; protecting the source, giving a failed "
                  "load a restart point, and holding the data as it was when a number is disputed "
                  "&mdash; have nothing to do with size. What a small source lets you skip is "
                  "incremental loading, not staging."},
            {"q": "Should staging tables have primary keys?",
             "a": "No. A staging table is a heap that is cleared and bulk-loaded each run; a key or "
                  "index turns a minimally logged load into a fully logged one, and a primary key "
                  "rejects the duplicate rows the source legitimately sent, which you wanted to see "
                  "downstream rather than lose at the door."},
            {"q": "Is staging the same as ODS?",
             "a": "No. An operational data store is integrated and current, meant to be queried "
                  "for operational reporting. Staging is a per-source copy meant to be read by the "
                  "warehouse load and nobody else."},
            {"q": "Can I do transformations in staging to save a step?",
             "a": "You can, and you will regret it the first time a number is wrong and you cannot "
                  "tell whether the source sent it or your transformation made it. Staging is "
                  "evidence. Transform in the layer that is allowed to have opinions."},
            {"q": "Is Medallion's bronze layer just staging?",
             "a": "Bronze is staging with one extra promise: it keeps what it received, unmodified, "
                  "rather than being truncated and refilled. Everything staging does, bronze does "
                  "too; bronze additionally works as an archive and can prove what arrived."},
        ],

        "related": [
            ("medallion-architecture.html", "Medallion architecture", "bronze is staging that never forgets"),
            ("data-vault-2-0.html", "Data Vault 2.0", "the other persistent-staging cousin"),
        ],
        "cta_h": "Generate the staging layer from a real database",
        "cta_p": "Netune reads a SQL Server database and writes the staging DDL and load "
                 "procedures the design needs &mdash; heaps, TABLOCK, the five type exceptions "
                 "handled at the boundary &mdash; and deploys them in the free edition.",
    },

    # ------------------------------------------------------------------ 3
    {
        "slug": "kimball-vs-data-vault.html",
        "short": "Kimball vs Data Vault",
        "oneline": "how to choose, and why the answer is often both",
        "crumb": "Kimball vs Data Vault",
        "title": "Kimball vs Data Vault: how to choose, and why the answer is usually both",
        "h1": "Kimball vs Data Vault: how to choose (and why the answer is usually both)",
        "meta": "Five questions that decide between a star schema and a Data Vault, a cost "
                "comparison, the architecture most real warehouses end up with, and the mistake of "
                "choosing Data Vault as a better Kimball.",
        "tw": "Count your source systems and ask whether you must prove what arrived. Then read this.",
        "keywords": "Kimball vs Data Vault, Data Vault vs star schema, dimensional model vs data "
                    "vault, when to use Data Vault, Data Vault or Kimball, data warehouse "
                    "architecture decision, raw vault with dimensional marts",
        "standfirst": "This is the comparison people search for most and the one most often "
                      "framed wrongly, because the two are not competing for the same job.",

        "answer": [
            "<strong>Count your source systems, and ask whether you must be able to prove what "
            "arrived.</strong>",
            "One or two systems, reporting questions, a team that needs results this quarter: "
            "<a href=\"/kimball-dimensional-modeling.html\">Kimball</a>, and you will be finished "
            "far sooner. Several systems that disagree about the same customer, schemas that keep "
            "changing, or an auditor: <a href=\"/data-vault-2-0.html\">Data Vault</a> as the "
            "integration layer &mdash; <em>and a star schema on top of it anyway</em>, because "
            "nobody reports off a raw vault.",
        ],

        "sections": [
            {
                "id": "job", "h2": "They are answers to different questions",
                "blocks": [
                    {"p": "Kimball answers: <em>how should this data be shaped so that people can "
                          "ask business questions of it?</em> Facts and dimensions, a declared "
                          "grain, one join per dimension, and every BI tool already knows the shape."},
                    {"p": "Data Vault answers: <em>how do we take in data from many changing "
                          "systems, keep all of it, and be able to say later exactly what we were "
                          "told and when?</em> Hubs, links and satellites, insert-only, and a shape "
                          "no analyst should query directly."},
                    {"p": "Put that way, the framing &ldquo;Kimball <em>or</em> Data Vault&rdquo; "
                          "is mostly a category error. One is a presentation model; the other is "
                          "an integration and history model. The real decision is whether you need "
                          "the second one at all &mdash; because you always need the first."},
                ],
            },
            {
                "id": "five", "h2": "The five questions that decide it",
                "blocks": [
                    {"h3": "1. How many source systems, and do they disagree?"},
                    {"p": "One system: nothing to integrate; a star schema straight from staging. "
                          "Several systems that each hold part of the same customer under "
                          "different keys: something has to reconcile them before a dimension can "
                          "exist, and that job is precisely what a vault (or an "
                          "<a href=\"/inmon-corporate-information-factory.html\">Inmon core</a>) "
                          "does. Kimball does not do it for you."},
                    {"h3": "2. Must you be able to prove what arrived?"},
                    {"p": "If &ldquo;what did we know about this account on the 3rd of March, and "
                          "when did we learn it&rdquo; is a question a regulator or an auditor will "
                          "ask, the raw vault&rsquo;s insert-only satellites answer it by "
                          "construction. A star schema can approximate it with type 2 dimensions "
                          "and never quite gets there, because facts and non-tracked attributes are "
                          "overwritten."},
                    {"h3": "3. How often does the source schema change?"},
                    {"p": "Rarely: any model works. Constantly: a vault absorbs a new column or a "
                          "new source by <em>adding tables</em>, and nothing loaded has to migrate. "
                          "A star absorbs it by being altered, and a changed grain means a rebuild. "
                          "This is the property people buy Data Vault for."},
                    {"h3": "4. How much history, and of what?"},
                    {"p": "History of a few grouping attributes &mdash; region, segment &mdash; is "
                          "a <a href=\"/scd-type-1-vs-type-2.html\">type 2 dimension</a>, and "
                          "Kimball handles it fine. History of <em>everything</em>, including things "
                          "nobody reports on yet, is the vault: it keeps all of it whether or not "
                          "anybody asked."},
                    {"h3": "5. How big is the team, and how soon do they need something?"},
                    {"p": "A vault is three tables where a star has one, plus a mart layer that is "
                          "not optional. A two-person team with a quarter to deliver should not "
                          "start one. A team of ten with a two-year mandate across nine systems "
                          "probably should."},
                ],
            },
            {
                "id": "table", "h2": "Side by side",
                "blocks": [
                    {"table": {
                        "head": ["", "Kimball (star schema)", "Data Vault 2.0"],
                        "rows": [
                            ["Primary job", "Presentation and reporting", "Integration and auditable history"],
                            ["Queried by analysts", "Yes &mdash; designed for it", "No &mdash; through marts only"],
                            ["Tables per entity", "1 (a dimension)", "3+ (hub, satellites, links)"],
                            ["History", "Per dimension, decided up front (SCD)", "Everything, automatically, insert-only"],
                            ["A new source system", "Conform it into existing dimensions", "Add hubs/satellites; touch nothing existing"],
                            ["Schema change", "Alter the star; rebuild if the grain moves", "Add a satellite"],
                            ["Time to first report", "Weeks", "Months (vault + marts)"],
                            ["Build cost", "Moderate", "High"],
                            ["Load complexity", "Lookups and SCD logic", "Hash keys; loads are order-free and parallel"],
                            ["Silent failure to fear", "Wrong grain", "Two hash expressions that differ by a trim"],
                            ["BI tool support", "Native", "None &mdash; needs the star on top"],
                        ],
                    }},
                ],
            },
            {
                "id": "both", "h2": "The architecture most real warehouses end up with",
                "blocks": [
                    {"code": "Sources  ->  Staging  ->  Raw Vault  ->  Business Vault  ->  Star schema marts  ->  BI\n"
                             "                         (integrate,      (derive,           (present:\n"
                             "                          keep everything)  conform)           facts & dimensions)"},
                    {"p": "Where the vault is warranted, this is what it looks like: the vault "
                          "integrates and remembers, the marts present. The marts are ordinary "
                          "Kimball &mdash; grain, conformed dimensions, type 2 where the past must "
                          "stay right &mdash; built from the vault rather than from staging, and "
                          "rebuildable whenever the questions change."},
                    {"p": "So &ldquo;Kimball vs Data Vault&rdquo; usually resolves to: Kimball, "
                          "certainly; Data Vault underneath it, if questions 1 to 3 say so. "
                          "Choosing the vault <em>instead of</em> a star only makes sense if nobody "
                          "needs to report yet, which is almost never true."},
                    {"note": "<strong>Where does staging go in this?</strong> Before both, and it "
                             "is the same layer either way &mdash; see "
                             "<a href=\"/what-is-a-staging-layer.html\">what a staging layer is "
                             "for</a>. A vault does not replace staging; the raw vault reads from it."},
                ],
            },
            {
                "id": "mistakes", "h2": "The mistakes each side makes",
                "blocks": [
                    {"h3": "Choosing Data Vault as “a better Kimball”"},
                    {"p": "It is not one. It is slower to deliver, harder to query, and three times "
                          "the tables, in exchange for integration, audit and change-absorption. A "
                          "team that adopts it for a single well-behaved source has paid for all of "
                          "that and received none of it."},
                    {"h3": "Building a vault with the marts as “phase two”"},
                    {"p": "Phase two gets cut. The team is left with a beautifully auditable "
                          "structure nobody can get an answer out of, and the vault gets blamed "
                          "for what was a project-planning failure. The marts are part of the "
                          "build."},
                    {"h3": "Building a star over six systems that disagree"},
                    {"p": "The opposite mistake. With no integration layer, every conflict between "
                          "systems &mdash; two customer numbers for one company, two spellings, two "
                          "hierarchies &mdash; gets resolved inside the dimension load, in "
                          "<code>CASE</code> expressions nobody documents, differently by each "
                          "developer. Within a year the star is an integration layer that was never "
                          "designed to be one."},
                    {"h3": "Treating the raw vault as a data source for analysts"},
                    {"p": "They will conclude the warehouse is broken, and from where they sit it "
                          "is. Every question is five joins and a newest-row filter per satellite. "
                          "Marts, or a business vault with views, or both."},
                ],
            },
            {
                "id": "migrate", "h2": "Moving from one to the other",
                "blocks": [
                    {"p": "<strong>Star to vault</strong> is the common direction and it is not a "
                          "rewrite: the existing star becomes the mart layer, a vault is built "
                          "underneath from staging, and the star&rsquo;s loads are re-pointed from "
                          "staging to the vault one dimension at a time. The reports do not change."},
                    {"p": "<strong>Vault to star</strong> alone &mdash; dropping the vault &mdash; "
                          "is rarer, and usually means the vault was never warranted. It is also "
                          "harmless: the marts are already Kimball; re-point their loads at "
                          "staging and let the vault go. Nothing about the presentation layer has "
                          "to move."},
                ],
            },
        ],

        "faq": [
            {"q": "Is Data Vault a replacement for a star schema?",
             "a": "No. A raw vault is an integration and history layer that is not built to be "
                  "queried; the readable layer on top of it is a star schema. Where a vault is "
                  "warranted, you build both. Where it is not, you build the star alone."},
            {"q": "When is Data Vault worth it?",
             "a": "Several source systems that disagree about the same entities, a schema that "
                  "changes often, or a genuine audit requirement to prove what arrived and when. "
                  "One or two of those and it starts paying for itself; none of them and it is "
                  "overhead."},
            {"q": "Can a small team use Data Vault?",
             "a": "It can, with generated loads and a clear plan for the marts, but it should ask "
                  "whether it needs to. A vault is three tables per entity plus a mart layer, and a "
                  "small team with a one-source warehouse gets the same reports from a star in a "
                  "fraction of the time."},
            {"q": "Which handles history better?",
             "a": "Data Vault keeps every version of everything by construction. Kimball keeps the "
                  "history you opt into, per dimension, with type 2. If the question is 'what did "
                  "we know and when', the vault; if it is 'keep last year's region on last year's "
                  "sales', type 2 in a star is enough and much cheaper."},
            {"q": "Can I migrate from Kimball to Data Vault later?",
             "a": "Yes, and it is the usual direction. The existing star becomes the mart layer, a "
                  "vault is built underneath it from staging, and the dimension loads are re-pointed "
                  "at the vault one at a time. The reports keep working throughout."},
        ],

        "related": [
            ("kimball-dimensional-modeling.html", "Kimball dimensional modelling", "the star schema in full"),
            ("data-vault-2-0.html", "Data Vault 2.0", "hubs, links, satellites and the hash-key invariant"),
            ("inmon-corporate-information-factory.html", "Inmon", "the other integration-layer answer"),
        ],
        "cta_h": "Let the database answer the five questions",
        "cta_p": "Netune measures how many systems feed a SQL Server database, whether the same "
                 "entity arrives under different keys, how often the schema appears to change and "
                 "whether real relationships exist &mdash; then scores Kimball and Data Vault "
                 "against each other on that evidence, reasons shown.",
    },
]
