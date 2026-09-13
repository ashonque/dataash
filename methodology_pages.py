"""What each of the eight per-methodology pages says.

`build-methodology-pages.py` is the shape; this is the words. They are apart
because the shape changes when the site does and the words change when
somebody learns something, and the two almost never change together.

**`good_when` and `poor_when` are copied from Netune's own rule files** -
`methodologies/<id>.py` in the Netune repository, where they are called
`GOOD_WHEN` and `POOR_WHEN`, and where `COST` holds the four cost lines.
Copied rather than imported, because this repository is the website and that
one is the product, and a website that will not build without a checkout of
the product beside it is a website nobody can fix from a laptop. The cost of
copying is that the two can drift; the honest mitigation is that anybody
changing a rule file's judgement should change it here in the same hour.
"""

PAGES = [

    # ------------------------------------------------------------------ 1
    {
        "slug": "kimball-dimensional-modeling.html",
        "short": "Kimball",
        "oneline": "Facts surrounded by dimensions, built for reporting",
        "crumb": "Kimball",
        "thing": "Dimensional modeling",
        "title": "Kimball dimensional modeling: the star schema, the grain, and what it costs",
        "short_title": "Kimball dimensional modelling",
        "h1": "Kimball dimensional modelling: the star schema, explained by what it costs",
        "meta": "What a Kimball star schema really is - facts, dimensions, the grain and SCD types - plus when it fits, when it does not, and the mistakes you cannot undo.",
        "tw": "Facts, dimensions, the grain and SCD types - and the mistakes you cannot cheaply undo.",
        "keywords": "Kimball dimensional modelling, star schema, fact table, dimension table, "
                    "slowly changing dimension, SCD type 2, grain, conformed dimension, "
                    "dimensional modeling SQL Server",
        "also": "star schema, dimensional modelling, fact and dimension tables, the Kimball method",
        "standfirst": "The most widely used way to model a warehouse, and the one most often "
                      "got wrong in the first week &mdash; because two of its decisions are "
                      "made early and cannot be cheaply undone.",

        "what": [
            "A Kimball model is built out of two kinds of table. A <strong>fact table</strong> "
            "holds the things you measure: an order line, a payment, a meter reading, a support "
            "ticket. A <strong>dimension table</strong> holds the things you slice by: customer, "
            "product, date, store, employee. Draw one fact with its dimensions around it and you "
            "get the shape everybody calls a star schema.",
            "What makes it the default is not elegance. It is that every business intelligence "
            "tool in existence &mdash; Power BI, Tableau, Looker, Excel&rsquo;s own pivot tables "
            "&mdash; expects this shape and is slower, or simply worse, on anything else. "
            "Choosing Kimball means the tooling is on your side.",
            "Ralph Kimball&rsquo;s own framing is worth keeping: the warehouse is modelled around "
            "<em>business processes</em>, not around departments and not around source systems. "
            "One star per process. Sales is a process. Returns is another. The marketing "
            "department is not a process, and a star built for a department is a star that has "
            "to be rebuilt when the org chart moves.",
        ],

        "shape": [
            {
                "h3": "The grain: the decision everything else rests on",
                "body": [
                    "The grain of a fact table is the answer to <em>what does one row mean?</em> "
                    "&mdash; and it has to be a sentence, not a shrug. &ldquo;One row is one line "
                    "of one order&rdquo; is a grain. &ldquo;Sales data&rdquo; is not.",
                    "It is decided first because everything downstream assumes it. Which "
                    "dimensions can attach, which measures can be added up, whether a count "
                    "means orders or items &mdash; all of it follows from the grain. Declare it "
                    "in writing before a single column is created, and put it in a comment at "
                    "the top of the table.",
                ],
            },
            {
                "h3": "The fact table",
                "body": [
                    "Narrow and long. Foreign keys to its dimensions, the numbers being measured, "
                    "and as little else as possible:",
                ],
                "code": "FactSales\n"
                        "  SalesKey        BIGINT IDENTITY   -- surrogate, not the source's key\n"
                        "  DateKey         INT      FK -> DimDate\n"
                        "  CustomerKey     INT      FK -> DimCustomer\n"
                        "  ProductKey      INT      FK -> DimProduct\n"
                        "  OrderNumber     NVARCHAR  -- a degenerate dimension: no table of its own\n"
                        "  Quantity        INT       -- additive\n"
                        "  LineTotal       DECIMAL   -- additive\n"
                        "  UnitPrice       DECIMAL   -- NOT additive: summing these means nothing",
                "list": [
                    "<strong>Additive</strong> measures can be summed across every dimension. "
                    "Quantity, revenue, cost.",
                    "<strong>Semi-additive</strong> measures sum across everything except time. "
                    "An account balance: adding January&rsquo;s to February&rsquo;s is nonsense, "
                    "but adding two accounts&rsquo; balances is fine.",
                    "<strong>Non-additive</strong> measures cannot be summed at all. A unit price, "
                    "a percentage, a ratio. Average them, or store the numerator and denominator "
                    "separately and divide at the end.",
                ],
            },
            {
                "h3": "The dimension table, and how much history it keeps",
                "body": [
                    "Wide and short, and deliberately denormalised: a product dimension carries "
                    "its subcategory and category as columns rather than as joins to two more "
                    "tables. Normalising them back out is called snowflaking, and it makes every "
                    "report pay for the tidiness.",
                    "The second unavoidable decision is what happens when an attribute changes "
                    "&mdash; a customer moves house. That is the <strong>slowly changing "
                    "dimension</strong> question, and in practice it has two answers worth "
                    "having:",
                ],
                "list": [
                    "<strong>Type 1</strong> overwrites. The old value is gone. Right when only "
                    "the current value ever matters, and when keeping the old one would be noise.",
                    "<strong>Type 2</strong> adds a new row and closes the old one, usually with "
                    "<code>ValidFrom</code>, <code>ValidTo</code> and <code>IsCurrent</code> "
                    "columns. History survives, so a report about last year keeps saying what it "
                    "said last year. This is the one people mean when they say &ldquo;SCD&rdquo;.",
                    "Types 3 and 6 exist &mdash; a previous-value column, and a hybrid of 1 and 2 "
                    "&mdash; and are far rarer than the literature suggests. Reach for them only "
                    "when you can say out loud which question they answer.",
                ],
            },
            {
                "h3": "Surrogate keys, and the row that catches the unknown",
                "body": [
                    "Every dimension gets a meaningless integer key of its own rather than reusing "
                    "the source system&rsquo;s. Two reasons that matter: type 2 history needs "
                    "several rows for one customer, so the source&rsquo;s key is no longer unique; "
                    "and when a second source system arrives with its own customer IDs, the "
                    "warehouse already has a key that belongs to neither.",
                    "Give every dimension an &ldquo;unknown&rdquo; row at key <code>-1</code>. A "
                    "fact whose customer cannot be resolved then points at that instead of being "
                    "dropped, and the row is still counted in the total &mdash; which is how you "
                    "find out the lookup is broken, rather than quietly reporting a smaller number.",
                ],
            },
        ],

        "fit_intro": "Kimball is a good default and a bad universal. It is the right answer "
                     "surprisingly often and the wrong one in ways that only show up months in.",
        "good_when": [
            "the business processes are understood and the grain can be agreed",
            "reporting and dashboards are the main purpose",
            "one or two source systems, changing slowly",
            "the team wants something analysts can query without help",
        ],
        "poor_when": [
            "sources change shape often - every change reaches the star",
            "many systems must be integrated before anyone agrees on meaning",
            "full history of every attribute is a hard requirement",
            "no one can yet say what one row of the main table means",
        ],
        "cost": [
            ("Build", "Moderate",
             "One star is a week or two of real work. The modelling questions take longer than "
             "the SQL."),
            ("Maintain", "Low",
             "A stable source means a stable star. New attributes are new columns."),
            ("Query", "Very easy",
             "One join per dimension, and every BI tool already understands the shape."),
            ("History", "Per dimension, decided up front",
             "Type 2 where the past must stay right. Retrofitting it later means reloading."),
        ],

        "mistakes": [
            {
                "h3": "Getting the grain wrong, then building on it",
                "body": [
                    "A fact table built at order level when the questions are about products "
                    "cannot answer them, and no amount of clever SQL recovers the detail that was "
                    "never stored. Going the other way &mdash; a grain finer than anything asked "
                    "for &mdash; costs storage and is otherwise harmless, so when in doubt, go "
                    "finer.",
                    "The tell is a fact table nobody can describe in one sentence. If two people "
                    "give two different answers to &ldquo;what is one row?&rdquo;, stop building.",
                ],
            },
            {
                "h3": "Letting the star snowflake",
                "body": [
                    "Source systems are normalised, so a straight copy gives you Product &rarr; "
                    "Subcategory &rarr; Category as three tables, and reports start joining "
                    "dimension to dimension. The whole point of the star is that they never have "
                    "to. Flatten the hierarchy into the child dimension &mdash; "
                    "<code>ProductCategoryName</code> as a column on <code>DimProduct</code> "
                    "&mdash; and accept the repetition.",
                    "The exception is a parent that a fact or a bridge points at directly. That "
                    "one is used at its own grain and keeps its table, even while its attributes "
                    "are also folded into the children.",
                ],
            },
            {
                "h3": "Keeping type 2 history of somebody else’s housekeeping",
                "body": [
                    "This one is quiet and expensive. If a type 2 dimension watches every column "
                    "for changes, and the source carries a <code>ModifiedDate</code> or a "
                    "<code>rowversion</code>, then every batch that touches the row opens a new "
                    "version of it. After a year the dimension holds a detailed history of the "
                    "source system&rsquo;s maintenance schedule and almost nothing about the "
                    "business.",
                    "So the change test has to be restricted to the attributes that actually "
                    "describe the business. Netune marks those columns <code>tracked</code> and "
                    "writes the others into the load anyway &mdash; they are stored, just not "
                    "watched &mdash; and names the ones it ignored in a comment, so the decision "
                    "is visible rather than mysterious.",
                ],
            },
        ],

        "versus": [
            {
                "h3": "Kimball or Galaxy?",
                "body": [
                    "There is no real choice here; <a href=\"/galaxy-schema.html\">Galaxy</a> is "
                    "what Kimball becomes when you model a second process. One fact table is a "
                    "star, several sharing the same dimensions is a constellation. The work it "
                    "adds is organisational rather than technical: every process has to agree on "
                    "what a customer is.",
                ],
            },
            {
                "h3": "Kimball or Data Vault?",
                "body": [
                    "Count your source systems, and ask whether you must be able to prove what "
                    "arrived. One system and reporting questions: Kimball, and you will be "
                    "finished far sooner. Several systems that disagree, schemas that keep "
                    "changing, or an audit requirement: "
                    "<a href=\"/data-vault-2-0.html\">Data Vault 2.0</a> &mdash; and then a star "
                    "on top of it anyway, because nobody reports off a raw vault.",
                ],
            },
            {
                "h3": "Kimball or One Big Table?",
                "body": [
                    "<a href=\"/one-big-table.html\">One Big Table</a> is a star with the joins "
                    "already done, which makes it faster to query and impossible to correct in "
                    "one place. For a single process on a columnar engine it is a reasonable "
                    "trade. For several processes sharing customers and products it is a trap: "
                    "the same customer&rsquo;s details end up in three wide tables that disagree.",
                ],
            },
        ],

        "netune_note": "Netune profiles a SQL Server database, classifies each table as a fact, "
                       "a dimension or a bridge from what is really in it, and &mdash; if a star "
                       "is what the data supports &mdash; generates the whole thing: the "
                       "dimensions with the SCD type each one argues for, the facts at a stated "
                       "grain, the surrogate keys, the unknown rows, and runnable T-SQL for all "
                       "of it. It shows the reasoning for every call so you can disagree with it.",

        "faq": [
            {
                "q": "What is the grain of a fact table?",
                "a": "What one row means, stated as a sentence: &ldquo;one row is one line of one "
                     "order&rdquo;. It is decided before anything else because every dimension, "
                     "every measure and every count depends on it. A fact table nobody can "
                     "describe in one sentence does not yet have a grain.",
            },
            {
                "q": "What is the difference between SCD type 1 and type 2?",
                "a": "Type 1 overwrites the old value, so history is lost and the dimension stays "
                     "one row per thing. Type 2 closes the old row and inserts a new one with "
                     "validity dates, so a report about last March still shows the address the "
                     "customer had in March. Use type 2 where the past must stay right; type 1 "
                     "where only today&rsquo;s value ever matters.",
            },
            {
                "q": "Why use surrogate keys instead of the source system's IDs?",
                "a": "Because type 2 history means one customer has several rows, so the source "
                     "key stops being unique &mdash; and because a second source system arrives "
                     "with its own IDs for the same customers. A meaningless integer key belongs "
                     "to the warehouse and survives both.",
            },
            {
                "q": "Is a star schema still relevant with a modern lakehouse?",
                "a": "Yes, and the two are not alternatives. "
                     "<a href=\"/medallion-architecture.html\">Medallion</a> says where a table "
                     "sits in the pipeline; Kimball says what a row means. Most lakehouse teams "
                     "end up modelling the gold layer dimensionally, which is doing both.",
            },
            {
                "q": "How many dimensions is too many?",
                "a": "There is no hard limit, but past a dozen on one fact it is worth checking "
                     "whether some are really attributes of others &mdash; a "
                     "&ldquo;dimension&rdquo; with three columns that only ever appears beside "
                     "another one usually belongs inside it.",
            },
        ],

        "cta_h": "See whether your database wants a star",
        "cta_p": "Netune reads a SQL Server database, works out which tables behave like facts "
                 "and which like dimensions, and generates the star with the history decisions "
                 "argued for rather than assumed. Free, runs on your machine, and nothing it "
                 "reads leaves it.",
    },

    # ------------------------------------------------------------------ 2
    {
        "slug": "inmon-corporate-information-factory.html",
        "short": "Inmon",
        "oneline": "An integrated 3NF core, with marts built on top",
        "crumb": "Inmon",
        "thing": "Corporate Information Factory",
        "title": "Inmon's Corporate Information Factory: the 3NF core and why the marts come after",
        "short_title": "Inmon — the CIF",
        "h1": "Inmon and the Corporate Information Factory: one integrated core, many marts",
        "meta": "Inmon's warehouse: a normalised, integrated core with dimensional marts on top. What it is for, when it beats Kimball, and why the marts are not optional.",
        "tw": "A normalised integrated core with dimensional marts on top - and why the marts are not a later phase.",
        "keywords": "Inmon, Corporate Information Factory, CIF, enterprise data warehouse, "
                    "3NF data warehouse, normalised core, Inmon vs Kimball, data mart, "
                    "single version of the truth",
        "also": "CIF, the enterprise data warehouse, the 3NF core, top-down data warehousing",
        "standfirst": "The approach that treats integration as the hard problem and reporting as "
                      "the easy one &mdash; and is right about that whenever more than one system "
                      "describes the same customer.",

        "what": [
            "Bill Inmon&rsquo;s warehouse has two layers with two different jobs. The "
            "<strong>core</strong> is normalised, integrated, and modelled on the business rather "
            "than on any one system: one customer, one definition, whatever each source calls "
            "them. The <strong>marts</strong> are dimensional, built on top of the core, and "
            "shaped for whoever is asking.",
            "Nobody queries the core directly. It is the single version of the truth and it is "
            "not built to be read &mdash; it is built to be <em>right</em>, and to stay right "
            "while systems come and go. The marts are the readable surface, and they are "
            "deliberately disposable: rebuild one whenever the questions change.",
            "This is the &ldquo;top-down&rdquo; half of the old Inmon-versus-Kimball argument. "
            "Model the enterprise first, then serve the departments. Kimball&rsquo;s bottom-up "
            "answer &mdash; serve one process well, then conform the dimensions &mdash; is faster "
            "to first value, and the two camps have long since stopped pretending either is "
            "universal.",
        ],

        "shape": [
            {
                "h3": "The core: third normal form, and time",
                "body": [
                    "The core looks like a well-designed operational schema with one difference: "
                    "it keeps history. Entities are normalised, relationships are real foreign "
                    "keys, and each entity version carries the period it was true for.",
                ],
                "code": "Ent_Customer\n"
                        "  CustomerKey     INT       -- surrogate, STABLE across every version\n"
                        "  EffectiveFrom   DATETIME2 -- key is (CustomerKey, EffectiveFrom)\n"
                        "  EffectiveTo     DATETIME2\n"
                        "  IsCurrent       BIT\n"
                        "  CustomerNumber  NVARCHAR  -- business key\n"
                        "  SourceSystem    NVARCHAR  -- business key: the same customer, twice over\n"
                        "  Name, Address, ...",
                "list": [
                    "The surrogate key <strong>identifies the customer</strong>; "
                    "<code>EffectiveFrom</code> identifies which version of them. A changed "
                    "customer reuses its key and gains a row. Only a genuinely new one takes a "
                    "new key.",
                    "A version is matched on the business key <em>and</em> the source system, "
                    "because the entire point of the core is that the same customer arrives from "
                    "two places and has to be reconciled rather than duplicated.",
                    "A key map records which source key became which core key &mdash; derived "
                    "from the core after it loads, since nothing in the source could say that "
                    "two IDs are the same person.",
                ],
            },
            {
                "h3": "The marts: current-only, and rebuilt",
                "body": [
                    "Mart dimensions read the core with <code>IsCurrent = 1</code> and are "
                    "replaced whole on each run. That sounds wasteful and is the correct trade: "
                    "the history lives in the core, so a mart has nothing to preserve, and a mart "
                    "that can be rebuilt from scratch is a mart you can change your mind about.",
                    "It does mean mart surrogate keys move between runs. Acceptable precisely "
                    "because the facts are rebuilt in the same run &mdash; but it is the reason "
                    "nothing outside the mart may store one of its keys.",
                ],
            },
            {
                "h3": "Where staging fits",
                "body": [
                    "Staging lands the source data, the core integrates it, the marts present it. "
                    "Three layers, and the middle one is the only one that is really Inmon "
                    "&mdash; the outer two are what every methodology does under different names.",
                ],
            },
        ],

        "fit_intro": "The question that decides this one is not technical. It is whether your "
                     "organisation is willing to argue about what a customer is, and then write "
                     "the answer down.",
        "good_when": [
            "several systems describe the same things differently",
            "the organisation wants one agreed definition of a customer or a product",
            "many departments will each want their own reporting",
            "there is time and appetite to model the business, not just the data",
        ],
        "poor_when": [
            "one source system and one reporting need",
            "results are wanted in weeks",
            "nobody is available to decide what the business terms mean",
            "the tables are unrelated extracts with nothing to integrate",
        ],
        "cost": [
            ("Build", "High",
             "Two layers, and the modelling of the core is a business exercise before it is a "
             "technical one."),
            ("Maintain", "Moderate",
             "A new source means integrating it into the core, which is real work by design."),
            ("Query", "Easy at the marts",
             "And deliberately hard at the core, which nobody is meant to query."),
            ("History", "In the core, by design",
             "Every entity version is kept, so the marts never have to ask the SCD question."),
        ],

        "mistakes": [
            {
                "h3": "Treating the marts as a later phase",
                "body": [
                    "The core alone reports on nothing. A project that spends its budget "
                    "perfecting the integration layer and leaves the marts for next year delivers "
                    "a warehouse that is finished and unusable at the same time &mdash; which is "
                    "how this methodology earned its reputation for slowness.",
                    "Budget for both, and get one thin mart working end to end before the core is "
                    "anywhere near complete.",
                ],
            },
            {
                "h3": "Building a core when there is nothing to integrate",
                "body": [
                    "With a single source system the integration layer is doing very little, and "
                    "a <a href=\"/kimball-dimensional-modeling.html\">star schema</a> reaches the "
                    "same reports with half the work. The core earns its cost when two systems "
                    "disagree about the same entity &mdash; and not before.",
                ],
            },
            {
                "h3": "Letting the core surrogate key move",
                "body": [
                    "The one invariant here is that a customer&rsquo;s key is the same in every "
                    "version of them. A load that renumbers from scratch turns the history into "
                    "several unrelated customers, silently, and every fact pointed at the old "
                    "numbers is now pointed at somebody else. Assign from the current maximum and "
                    "reuse the existing key wherever the business key matches.",
                ],
            },
        ],

        "versus": [
            {
                "h3": "Inmon or Kimball?",
                "body": [
                    "The honest answer is: how many source systems, and how much time. "
                    "<a href=\"/kimball-dimensional-modeling.html\">Kimball</a> gives reports "
                    "sooner and handles one or two well-behaved sources beautifully. Inmon "
                    "handles the case where the sources contradict each other and somebody has to "
                    "decide who is right &mdash; and that decision has to live somewhere other "
                    "than in each report.",
                    "In practice most large warehouses end up with both: an integrated core and "
                    "dimensional marts. That is Inmon&rsquo;s design, and it is also what a "
                    "Kimball shop builds after its fifth star.",
                ],
            },
            {
                "h3": "Inmon or Data Vault?",
                "body": [
                    "Both put an integration layer between the sources and the reports, and both "
                    "keep history there. The difference is what happens when a source changes "
                    "shape: <a href=\"/data-vault-2-0.html\">Data Vault</a> absorbs it by adding "
                    "tables, while an Inmon core absorbs it by somebody remodelling the entity. "
                    "Vault is more mechanical and less opinionated; the core is more readable and "
                    "asks more of its modellers.",
                ],
            },
        ],

        "netune_note": "Netune scores Inmon against what it measures in your database &mdash; "
                       "how many source systems appear to feed it, whether the same entity shows "
                       "up under different keys, how connected the tables are &mdash; and if it "
                       "is the model you pick, generates the core with its stable surrogate keys "
                       "and effective dates, the key map, and the current-only marts on top.",

        "faq": [
            {
                "q": "What is the difference between Inmon and Kimball?",
                "a": "Inmon builds a normalised, integrated core first and serves departments "
                     "from marts on top of it; Kimball builds a dimensional model per business "
                     "process and conforms the dimensions between them. Inmon is slower to first "
                     "report and better where several systems disagree about the same entity.",
            },
            {
                "q": "Can I query the Inmon core directly?",
                "a": "You can, and you are not meant to. It is normalised and versioned, so every "
                     "question costs joins and a filter on the effective dates. That is what the "
                     "marts are for &mdash; and it is why building the core without them leaves "
                     "you with nothing anybody can use.",
            },
            {
                "q": "Is the Corporate Information Factory the same as an enterprise data warehouse?",
                "a": "Near enough in everyday use. The CIF is Inmon's fuller architecture &mdash; "
                     "core, marts, operational data store, and the metadata around them &mdash; "
                     "and &ldquo;enterprise data warehouse&rdquo; usually means the integrated "
                     "core at the middle of it.",
            },
            {
                "q": "Does an Inmon core need slowly changing dimensions?",
                "a": "No, and that is one of its advantages. The core keeps every version of "
                     "every entity by construction, so there is no per-dimension history decision "
                     "to make. The marts are current-only and rebuilt, so they have nothing to "
                     "keep.",
            },
        ],

        "cta_h": "See whether your data has anything to integrate",
        "cta_p": "Netune measures how many systems feed your database, whether the same entity "
                 "arrives twice under different keys, and how much of it is really connected "
                 "&mdash; the evidence that decides whether a core is worth its cost.",
    },

    # ------------------------------------------------------------------ 3
    {
        "slug": "data-vault-2-0.html",
        "short": "Data Vault 2.0",
        "oneline": "Hubs, links and satellites; nothing is ever updated",
        "crumb": "Data Vault 2.0",
        "thing": "Data Vault modeling",
        "title": "Data Vault 2.0 explained: hubs, links, satellites and the hash key",
        "short_title": "Data Vault 2.0",
        "h1": "Data Vault 2.0: hubs, links and satellites, and what they really cost",
        "meta": "What a hub, a link and a satellite hold, why the raw vault is insert-only, how hash keys make loads order-free, and why nobody should query a raw vault.",
        "tw": "Hubs, links, satellites, hash keys and the ghost row - and why the marts are part of the project.",
        "keywords": "Data Vault 2.0, hub link satellite, raw vault, business vault, hash key, "
                    "HashDiff, insert-only data warehouse, auditability, Dan Linstedt, "
                    "Data Vault vs Kimball",
        "also": "DV2.0, hubs links and satellites, the raw vault, Linstedt’s model",
        "standfirst": "Built for the case where the warehouse has to be able to say exactly what "
                      "it was told, and when &mdash; and where the sources will not stop changing "
                      "shape.",

        "what": [
            "Data Vault splits every entity into three kinds of table. A <strong>hub</strong> "
            "holds a business key and nothing else &mdash; the customer number, the product code. "
            "A <strong>link</strong> holds a relationship between hubs. A <strong>satellite</strong> "
            "holds everything descriptive, hanging off a hub or a link, with a load date.",
            "The rule that makes it work: <strong>nothing is ever updated or deleted</strong>. A "
            "satellite gets a new row when the incoming data differs from the newest row already "
            "there, and the old row stays exactly as it was. The warehouse can therefore always "
            "answer &ldquo;what did we know about this customer on the 3rd of March, and when did "
            "we learn it?&rdquo;",
            "The pay-off is what happens when a source changes. Adding a system, or a new set of "
            "attributes, means adding tables rather than rewriting existing ones &mdash; nothing "
            "already loaded has to be migrated. That single property is what people buy Data "
            "Vault for, and it is genuinely rare.",
        ],

        "shape": [
            {
                "h3": "The three table types",
                "code": "Hub_Customer\n"
                        "  Customer_HK     BINARY(32)  -- hash of the business key\n"
                        "  CustomerNumber  NVARCHAR    -- the business key itself\n"
                        "  LoadDate, RecordSource\n"
                        "\n"
                        "Link_Order_Customer\n"
                        "  Order_Customer_HK  BINARY(32)   -- hash of both parent keys\n"
                        "  Order_HK, Customer_HK           -- the hubs it joins\n"
                        "  LoadDate, RecordSource\n"
                        "\n"
                        "Sat_Customer\n"
                        "  Customer_HK     BINARY(32)   -- key is (Customer_HK, LoadDate)\n"
                        "  LoadDate        DATETIME2\n"
                        "  HashDiff        BINARY(32)   -- hash of every descriptive column\n"
                        "  Name, Address, Segment, ...",
                "after": [
                    "<code>HashDiff</code> is how a satellite decides whether anything changed: "
                    "hash all the descriptive columns, compare with the newest stored row, insert "
                    "only if they differ. It is cheaper than comparing forty columns and it "
                    "cannot be fooled by column order.",
                ],
            },
            {
                "h3": "Why hash keys, and the invariant nobody may break",
                "body": [
                    "The hash key is the business key put through a hash function. That means a "
                    "satellite can <em>recompute</em> its parent&rsquo;s key from its own incoming "
                    "row rather than looking the hub up &mdash; so the satellite can load before "
                    "the hub does and still land on the right key. Loads become order-free and "
                    "parallel, which on a large vault is the difference between a nightly window "
                    "and no nightly window.",
                    "The price is an invariant you cannot be casual about: <strong>every "
                    "expression that computes a key must be character-for-character "
                    "identical</strong>. One load that trims the key and another that does not "
                    "produce different hashes, the join finds nothing, and there is no error "
                    "&mdash; just an empty warehouse. Normalise once (trim, upper-case, a known "
                    "placeholder for NULL) and write that expression in exactly one place.",
                ],
            },
            {
                "h3": "The ghost row",
                "body": [
                    "Every hub gets a row for &ldquo;unknown&rdquo;, whose key is what a NULL "
                    "business key hashes to. Without it, a link involving a missing reference has "
                    "to be dropped, and the transaction disappears from the warehouse entirely. "
                    "With it, the row survives and points somewhere honest. It is Kimball&rsquo;s "
                    "<code>-1</code> member under another name.",
                ],
            },
            {
                "h3": "The business vault and the marts",
                "body": [
                    "The raw vault holds what arrived. Anything calculated, conformed or "
                    "interpreted goes in a <strong>business vault</strong> beside it, and the "
                    "readable layer is a set of dimensional marts on top of that. This is not an "
                    "optional extra phase &mdash; it is how anybody gets an answer out.",
                ],
            },
        ],

        "fit_intro": "Data Vault is the most demanding model here and the most often chosen for "
                     "the wrong reason. It is not a better Kimball; it solves a different problem.",
        "good_when": [
            "several source systems must be brought together",
            "full history is required, including of things nobody reports on yet",
            "sources change shape often and the warehouse must absorb it",
            "auditability matters more than convenience",
        ],
        "poor_when": [
            "a small model with one source and no history requirement",
            "the team is small - the table count and load logic are heavy",
            "analysts will query it directly, which they should not",
            "results are needed in weeks rather than months",
        ],
        "cost": [
            ("Build", "High",
             "Three tables where other models have one, plus a mart layer that is not optional."),
            ("Maintain", "Moderate",
             "New sources add tables rather than changing them, which is the whole point."),
            ("Query", "Hard without marts",
             "A question that is one join in a star is five or six in a raw vault."),
            ("History", "Complete, automatically",
             "Insert-only is the mechanism, so there is no per-table history decision at all."),
        ],

        "mistakes": [
            {
                "h3": "Letting analysts near the raw vault",
                "body": [
                    "It is not built to be read, and a team that has to query it directly will "
                    "conclude the warehouse is broken &mdash; reasonably. Every question means "
                    "joining hubs to links to satellites and filtering each satellite to its "
                    "newest row. Plan the marts as part of the project, not as a phase two that "
                    "gets cut.",
                ],
            },
            {
                "h3": "Two expressions for one hash",
                "body": [
                    "Covered above because it is the failure mode that costs the most time: it "
                    "produces no error, no warning and no rows. If you write vault loads by hand, "
                    "put the key expression in one place &mdash; a function, a view, a generator "
                    "&mdash; and never type it a second time.",
                ],
            },
            {
                "h3": "Hashing a concatenation that silently truncates",
                "body": [
                    "A link key hashes several business keys joined together. In SQL Server, "
                    "concatenating sized string types caps the result at 4000 characters, so a "
                    "link over several hubs with long keys truncates before it hashes &mdash; "
                    "only for the long ones, which is the worst possible distribution of a bug. "
                    "Widen the first part to <code>NVARCHAR(MAX)</code> and the problem goes away.",
                ],
            },
        ],

        "versus": [
            {
                "h3": "Data Vault or Kimball?",
                "body": [
                    "If you are choosing between them you are probably choosing both: Data Vault "
                    "for the integration and history, a "
                    "<a href=\"/kimball-dimensional-modeling.html\">star schema</a> on top for "
                    "the reporting. Choosing Data Vault <em>instead</em> of a star only makes "
                    "sense if nobody needs to report yet, which is rarely true.",
                ],
            },
            {
                "h3": "Data Vault or Inmon?",
                "body": [
                    "Both are integration layers with history. "
                    "<a href=\"/inmon-corporate-information-factory.html\">Inmon&rsquo;s core</a> "
                    "asks people to model the business and rewards them with something readable; "
                    "the vault asks for far less modelling judgement and rewards you with "
                    "something that absorbs change mechanically. Pick the vault when the sources "
                    "change faster than the committee meets.",
                ],
            },
            {
                "h3": "Data Vault or Anchor Modeling?",
                "body": [
                    "<a href=\"/anchor-modeling.html\">Anchor</a> takes the same idea further "
                    "&mdash; one table per attribute rather than a satellite of several &mdash; "
                    "and pays for it in joins. Anchor is the stricter, more academic cousin; the "
                    "vault is the one with more industry tooling around it.",
                ],
            },
        ],

        "netune_note": "Netune scores Data Vault on what it can measure &mdash; how many systems "
                       "feed the database, how often the schema seems to change, whether there "
                       "are real relationships for links to hold &mdash; and, if you choose it, "
                       "generates the hubs, links and satellites with one definition of every "
                       "hash key, the ghost rows computed by that same expression, and the load "
                       "order the foreign keys require.",

        "faq": [
            {
                "q": "What is the difference between a hub, a link and a satellite?",
                "a": "A hub holds a business key and nothing else. A link holds a relationship "
                     "between hubs. A satellite holds the descriptive columns, hanging off a hub "
                     "or a link, with a load date &mdash; and gets a new row whenever the "
                     "description changes.",
            },
            {
                "q": "Why is the raw vault insert-only?",
                "a": "Because that is how it keeps history and how it stays auditable. Nothing is "
                     "updated or deleted, so the warehouse can always say what it was told and "
                     "when. It is also why Data Vault has no slowly-changing-dimension question "
                     "to answer.",
            },
            {
                "q": "Do I still need a star schema if I use Data Vault?",
                "a": "In practice, yes. The raw vault is not built to be queried &mdash; every "
                     "question costs several joins and a newest-row filter per satellite &mdash; "
                     "so the readable layer is dimensional marts built on top. Budget for them "
                     "from the start.",
            },
            {
                "q": "What is a HashDiff?",
                "a": "A hash of all the descriptive columns in a satellite row. The load compares "
                     "it with the newest stored row for that key and inserts only when they "
                     "differ, which is cheaper than comparing every column and is not confused by "
                     "column order.",
            },
            {
                "q": "Is Data Vault overkill for a small warehouse?",
                "a": "Usually, yes. With one source, no audit requirement and a stable schema, it "
                     "gives you three tables where you needed one and a mart layer you would not "
                     "otherwise have built. Its costs are paid back by many sources, frequent "
                     "schema change, or a regulator.",
            },
        ],

        "cta_h": "See whether your data has anything for links to hold",
        "cta_p": "Netune measures the relationships, the key structure and the apparent number of "
                 "source systems in a real SQL Server database, and scores Data Vault against "
                 "seven alternatives on that evidence &mdash; with the reasons shown.",
    },

    # ------------------------------------------------------------------ 4
    {
        "slug": "medallion-architecture.html",
        "short": "Medallion",
        "oneline": "Bronze, silver, gold — a pipeline, not a model",
        "crumb": "Medallion",
        "thing": "Medallion architecture",
        "title": "Medallion architecture: what bronze, silver and gold are actually for",
        "short_title": "Medallion architecture",
        "h1": "Medallion architecture: bronze, silver and gold, and what it does not do",
        "meta": "What belongs in bronze, silver and gold, why bronze must never be cleaned, and the thing Medallion does not give you: it organises work, it does not model.",
        "tw": "Bronze, silver, gold - what each layer is for, and the one thing Medallion does not give you.",
        "keywords": "Medallion architecture, bronze silver gold, lakehouse, Databricks, "
                    "Microsoft Fabric, multi-hop architecture, data lakehouse layers, "
                    "Medallion vs Kimball, delta lake",
        "also": "the multi-hop architecture, bronze/silver/gold layers, the lakehouse pattern",
        "standfirst": "The default shape of a modern lakehouse pipeline, and the one that most "
                      "often gets adopted in the belief that it answers a question it does not "
                      "even ask.",

        "what": [
            "Medallion splits a pipeline into three layers. <strong>Bronze</strong> holds "
            "everything exactly as it arrived, unmodified. <strong>Silver</strong> holds it "
            "cleaned, typed and deduplicated. <strong>Gold</strong> holds business-ready tables "
            "that people actually query.",
            "It came out of the Databricks world and is now the house style of most lakehouse "
            "projects, Microsoft Fabric included. Its real virtue is that it makes the state of "
            "every table obvious from where it sits: nobody has to ask whether a given table has "
            "been cleaned yet.",
            "And here is the part worth being direct about, because skipping it causes most of "
            "the disappointment: <strong>Medallion organises the work; it does not model the "
            "business.</strong> It tells you where a table sits in a pipeline. It does not tell "
            "you what a row means, what the grain is, or how history is kept. Those questions "
            "still have to be answered &mdash; in gold, usually by "
            "<a href=\"/kimball-dimensional-modeling.html\">modelling it dimensionally</a>.",
        ],

        "shape": [
            {
                "h3": "Bronze: prove what arrived",
                "body": [
                    "Bronze is a landing zone with a memory. Typically the source columns as they "
                    "came, plus a few of its own:",
                ],
                "code": "Bronze_Customer\n"
                        "  ...every source column, as it arrived...\n"
                        "  _ingested_at    DATETIME2\n"
                        "  _source_system  NVARCHAR\n"
                        "  _batch_id       NVARCHAR\n"
                        "  _raw_hash       BINARY(32)   -- hash of the row EXACTLY as received",
                "list": [
                    "<strong>Do not clean it, and do not normalise the hash input.</strong> No "
                    "trimming, no upper-casing. The entire point of bronze is that it can prove "
                    "what was received, and a hash computed over tidied-up input cannot.",
                    "Duplicate business keys belong here, and so do rows with no key at all. "
                    "Deduplicating is silver&rsquo;s job.",
                    "It is usually a heap with no keys and no indexes, loaded in bulk. There is "
                    "no candidate key to declare, and an index would only slow the load.",
                ],
            },
            {
                "h3": "Silver: one row per thing, with history",
                "body": [
                    "Silver reads bronze and nothing else. It types the columns properly, "
                    "deduplicates on the business key &mdash; newest ingest wins, which is a real "
                    "tie-break rather than an arbitrary one &mdash; and keeps history with "
                    "validity dates.",
                    "That makes silver&rsquo;s primary key the <strong>business key plus the "
                    "moment the version started</strong>, not the business key alone. The same "
                    "shape as an Inmon core, but on the source&rsquo;s own key, because not "
                    "inventing a surrogate is part of the point of this layer.",
                    "Rows with no business key stay in bronze. Nothing can key them, so nothing "
                    "downstream could join them anyway &mdash; and quietly passing them along "
                    "makes the counts wrong in a way nobody traces.",
                ],
            },
            {
                "h3": "Gold: the layer that still needs a model",
                "body": [
                    "Gold reads silver, never bronze. It is aggregated, filtered to the current "
                    "and valid rows, and shaped for a question. It is also where the modelling "
                    "you skipped arrives: in practice most gold layers are star schemas, which "
                    "means most Medallion projects are doing Kimball as well, not instead.",
                    "A gold table is usually better off with a clustered index than a primary "
                    "key: it is rebuilt whole and grouped by period and by whatever it slices on, "
                    "and a grouping column may legitimately be NULL &mdash; which a primary key "
                    "would refuse.",
                ],
            },
        ],

        "fit_intro": "Medallion is easy to adopt and hard to regret, which is exactly why it is "
                     "worth being clear about what it leaves undone.",
        "good_when": [
            "the sources are messy and cleaning has to be visible and auditable",
            "the platform is a lakehouse - Databricks, Fabric, Snowflake",
            "different teams want to work at different levels of rawness",
            "you want to start delivering before the modelling questions are settled",
        ],
        "poor_when": [
            "the sources are already clean and well modelled",
            "a small model where three layers is two too many",
            "the business wants conformed dimensions, which this does not give you",
            "storage cost matters - the same data is held three times",
        ],
        "cost": [
            ("Build", "Low to moderate",
             "Each hop is simple on its own. The work is in silver's cleaning rules."),
            ("Maintain", "Moderate",
             "Three layers to keep in step, and a schema change ripples through all three."),
            ("Query", "Easy at gold",
             "Assuming gold was modelled. If it was not, it is as hard as whatever is in there."),
            ("History", "Whatever bronze keeps",
             "Bronze is the archive; silver's validity dates are what anybody actually queries."),
        ],

        "mistakes": [
            {
                "h3": "Cleaning bronze “just a little”",
                "body": [
                    "Trimming whitespace on the way in feels harmless and destroys the only thing "
                    "bronze was for. The moment bronze differs from what was sent, it can no "
                    "longer settle an argument with the source system &mdash; which is the "
                    "situation you built it for.",
                ],
            },
            {
                "h3": "Expecting gold to model itself",
                "body": [
                    "Teams adopt Medallion, build bronze and silver competently, and then "
                    "discover that &ldquo;gold&rdquo; is not a design &mdash; it is an empty "
                    "schema with a colour. The grain, the conformed dimensions and the history "
                    "questions are all still waiting. Decide the gold model at the start; "
                    "Medallion will not decide it for you.",
                ],
            },
            {
                "h3": "Reading bronze from gold",
                "body": [
                    "It happens when something is missing from silver and a deadline is close, "
                    "and it quietly removes every guarantee the middle layer was making. If gold "
                    "needs something bronze has, the fix belongs in silver.",
                ],
            },
        ],

        "versus": [
            {
                "h3": "Medallion or Kimball?",
                "body": [
                    "Not really a choice &mdash; they answer different questions. Medallion says "
                    "where a table sits in the pipeline; "
                    "<a href=\"/kimball-dimensional-modeling.html\">Kimball</a> says what a row "
                    "means. The common and correct arrangement is Medallion for the pipeline with "
                    "a star schema in gold.",
                ],
            },
            {
                "h3": "Medallion or Data Vault?",
                "body": [
                    "Bronze and a <a href=\"/data-vault-2-0.html\">raw vault</a> overlap: both "
                    "keep what arrived so it can be proven later. The vault also integrates "
                    "across systems and keeps attribute-level history in a queryable structure, "
                    "which bronze does not. On a lakehouse with several systems, people often run "
                    "both &mdash; bronze for the raw files, a vault in silver.",
                ],
            },
            {
                "h3": "Is Medallion the same as staging?",
                "body": [
                    "Bronze is a staging layer with one extra promise: it keeps what it received, "
                    "unmodified, rather than being truncated and refilled each run. Everything "
                    "else staging does &mdash; keeping the transformation off the production "
                    "system, giving a failed load somewhere to restart &mdash; bronze does too.",
                ],
            },
        ],

        "netune_note": "Netune scores Medallion alongside the seven others and, if you pick it, "
                       "generates all three layers for SQL Server &mdash; bronze with its "
                       "untouched raw hash, silver deduplicated by newest ingest with validity "
                       "dates, and gold filtered to the current and valid rows. Which is also a "
                       "quick way to see how much modelling gold still needs.",

        "faq": [
            {
                "q": "What goes in bronze, silver and gold?",
                "a": "Bronze holds the data exactly as it arrived, unmodified, with ingestion "
                     "metadata. Silver holds it typed, deduplicated on the business key and "
                     "versioned with validity dates. Gold holds business-ready tables, usually "
                     "aggregated and usually modelled dimensionally.",
            },
            {
                "q": "Is Medallion architecture a data modelling methodology?",
                "a": "No, and this is the most useful thing to know about it. It organises a "
                     "pipeline into layers; it does not say what a row means, what the grain is, "
                     "or how history is kept. Those questions are answered in gold, typically "
                     "with a star schema.",
            },
            {
                "q": "Can I skip silver?",
                "a": "On genuinely clean, well-modelled sources, some teams do &mdash; and then "
                     "the first messy source arrives and the cleaning lands in gold, where it is "
                     "invisible and repeated. Silver is cheap while the pipeline is small; "
                     "retrofitting it is not.",
            },
            {
                "q": "Does Medallion work outside a lakehouse?",
                "a": "Yes. The three layers are just schemas or databases, and the pattern works "
                     "perfectly well on SQL Server. The one thing that changes is the storage "
                     "bill: holding the same data three times is cheap on object storage and a "
                     "real cost on a traditional database.",
            },
        ],

        "cta_h": "See what your gold layer would have to be",
        "cta_p": "Netune reads a SQL Server database, scores Medallion against seven other "
                 "models on the evidence, and generates bronze, silver and gold as runnable "
                 "T-SQL &mdash; including the modelling decisions gold cannot avoid.",
    },

    # ------------------------------------------------------------------ 5
    {
        "slug": "galaxy-schema.html",
        "short": "Galaxy",
        "oneline": "Several stars sharing conformed dimensions",
        "crumb": "Galaxy",
        "thing": "Fact constellation schema",
        "title": "Galaxy schema (fact constellation): conformed dimensions across several stars",
        "short_title": "Galaxy schema",
        "h1": "The galaxy schema: several fact tables, one set of conformed dimensions",
        "meta": "What a galaxy schema or fact constellation is, what makes a dimension conformed, and why the hard part is an agreement rather than a join. With the bus matrix.",
        "tw": "Several stars, one customer table - and why conforming a dimension is an organisational act.",
        "keywords": "galaxy schema, fact constellation, conformed dimension, bus matrix, "
                    "multiple fact tables, star schema vs galaxy schema, Kimball bus "
                    "architecture, shared dimensions",
        "also": "fact constellation, the Kimball bus architecture, conformed dimensions, multi-star schema",
        "standfirst": "What a star schema becomes the moment you model a second business process "
                      "&mdash; and the point at which the difficult questions stop being "
                      "technical.",

        "what": [
            "A galaxy schema is several fact tables sharing the same dimension tables. One "
            "customer table serving sales, returns and support; one product table serving all "
            "three; one calendar serving everything. Draw it and you get several stars with their "
            "points touching, which is where the name comes from.",
            "A dimension used by more than one fact is <strong>conformed</strong>. That word "
            "means something precise and demanding: every process that uses it agrees on what it "
            "means, what its grain is, and what its attributes are called. A customer table that "
            "sales and support both read but interpret differently is not conformed &mdash; it is "
            "shared, which is a different and more dangerous thing.",
            "Conformed dimensions are what let a question cross between processes. &ldquo;Which "
            "customers bought the most and complained the most?&rdquo; is answerable only if both "
            "facts point at the same customer table with the same key. Without that, the answer "
            "has to be assembled by hand, and two people assembling it get two answers.",
        ],

        "shape": [
            {
                "h3": "The shape itself",
                "code": '        DimDate    DimCustomer    DimProduct    DimStore\n           |            |              |           |\n   +-------+------------+--------------+-----------+\n   |                    |                          |\nFactSales          FactReturns          FactSupportTicket\n(one order line)   (one returned line)  (one ticket)',
                "after": [
                    "Every fact keeps its own grain &mdash; one row of FactSales is a sales line, "
                    "one row of FactSupportTicket is a ticket &mdash; and that is fine and "
                    "expected. What must match is the dimensions, and the keys into them.",
                ],
            },
            {
                "h3": "The bus matrix",
                "body": [
                    "The bus matrix is the one-page artefact that makes a galaxy manageable: "
                    "processes down the side, dimensions across the top, a mark in every cell "
                    "where that process uses that dimension.",
                ],
                "code": "                  Date  Customer  Product  Store  Employee\n"
                        "Sales               X       X         X       X\n"
                        "Returns             X       X         X       X\n"
                        "Support ticket      X       X                        X\n"
                        "Inventory           X                 X       X",
                "list": [
                    "It shows at a glance which dimensions are load-bearing &mdash; the ones with "
                    "marks in every row are the ones that must be got right first.",
                    "It shows what is <em>not</em> shared, which is just as useful: a dimension "
                    "used by one process does not need conforming and does not need the meeting.",
                    "It is a planning tool, so it is worth keeping in the warehouse itself. What "
                    "uses what is a fact about the design rather than about the source data, so "
                    "it can be generated from the model rather than maintained by hand.",
                ],
            },
            {
                "h3": "Conforming, in practice",
                "body": [
                    "Two dimensions are conformed if one is identical to the other, or if one is "
                    "a strict subset of the other &mdash; the same attributes, the same meanings, "
                    "a rollup rather than a rewrite. A monthly dimension conformed to a daily one "
                    "is fine. A &ldquo;customer&rdquo; that means an account in one place and a "
                    "person in another is not, and no amount of key management fixes it.",
                ],
            },
        ],

        "fit_intro": "A galaxy is where a warehouse naturally arrives. The question is whether "
                     "the organisation is ready for what conforming requires of it.",
        "good_when": [
            "more than one business process needs reporting",
            "the same customer or product appears in several of them",
            "people want to compare across processes, not just within one",
            "the organisation can agree on one definition per dimension",
        ],
        "poor_when": [
            "there is only one business process worth modelling",
            "nobody can agree what a customer is across departments",
            "the facts genuinely share nothing",
            "the team wants something delivered this month",
        ],
        "cost": [
            ("Build", "Moderate to high",
             "The second star is cheaper than the first, except for the agreements it forces."),
            ("Maintain", "Low",
             "A conformed dimension is maintained once and improves every process at once."),
            ("Query", "Very easy",
             "The same star-shaped queries, and now they can cross between processes."),
            ("History", "Per dimension, decided once and shared",
             "Which is an advantage: the SCD choice is made once, not once per star."),
        ],

        "mistakes": [
            {
                "h3": "Sharing a dimension that was never conformed",
                "body": [
                    "This is the failure the whole model turns on. Two departments point at one "
                    "customer table while meaning different things by &ldquo;active&rdquo;, and "
                    "every cross-process report is now confidently wrong. It produces no error "
                    "and no warning &mdash; just numbers that do not reconcile, argued about in "
                    "meetings for months.",
                    "Conforming is an organisational act. Get the definition written down and "
                    "agreed before the dimension is shared, not after the first argument.",
                ],
            },
            {
                "h3": "Building all the stars at once",
                "body": [
                    "The bus matrix tempts people into treating the whole grid as one project. "
                    "Kimball&rsquo;s own advice is the opposite and it has held up: deliver one "
                    "process end to end, conform its dimensions properly, then add the next "
                    "process against those dimensions. Each star is usable the day it lands.",
                ],
            },
            {
                "h3": "Forcing a shared dimension where the facts share nothing",
                "body": [
                    "If two processes genuinely have no customers or products in common, they are "
                    "two stars that happen to live in one database, and inventing a conformed "
                    "dimension over them adds meetings and no answers.",
                ],
            },
        ],

        "versus": [
            {
                "h3": "Galaxy or Kimball?",
                "body": [
                    "Galaxy <em>is</em> <a href=\"/kimball-dimensional-modeling.html\">Kimball</a>, "
                    "at the point where a second business process arrives. Everything true of a "
                    "star &mdash; grain, additivity, surrogate keys, SCD types &mdash; is true "
                    "here, with conforming added on top. If you have one fact table, you have a "
                    "star, and there is nothing further to decide.",
                ],
            },
            {
                "h3": "Galaxy or Inmon?",
                "body": [
                    "Both answer &ldquo;how do several processes agree on one customer?&rdquo;. "
                    "<a href=\"/inmon-corporate-information-factory.html\">Inmon</a> answers it in "
                    "a normalised core that nobody queries, with marts on top. A galaxy answers "
                    "it directly in the dimensional layer. Inmon scales better across many source "
                    "systems; a galaxy gets you reporting sooner.",
                ],
            },
        ],

        "netune_note": "Netune counts the business processes it can see, works out which "
                       "dimensions more than one of them would point at, and scores a galaxy "
                       "against the alternatives on that. If you build one, it generates the "
                       "shared dimensions once, each fact against them, and fills the bus matrix "
                       "from the design itself rather than asking you to maintain it.",

        "faq": [
            {
                "q": "What is the difference between a star schema and a galaxy schema?",
                "a": "A star schema has one fact table with its dimensions around it. A galaxy "
                     "schema &mdash; also called a fact constellation &mdash; has several fact "
                     "tables sharing the same dimension tables, so questions can cross between "
                     "business processes.",
            },
            {
                "q": "What is a conformed dimension?",
                "a": "A dimension that several fact tables use, where every process agrees on what "
                     "it means, what its grain is and what its attributes are called. Either "
                     "identical everywhere, or a strict subset &mdash; a rollup, never a rewrite. "
                     "Sharing a table without that agreement is how cross-process reports come "
                     "out wrong.",
            },
            {
                "q": "What is a bus matrix?",
                "a": "A one-page grid of business processes against dimensions, with a mark where "
                     "each process uses each dimension. It shows which dimensions are load-bearing, "
                     "which need conforming, and what the delivery order should be.",
            },
            {
                "q": "Should I build all the stars at once?",
                "a": "No. Deliver one process end to end, conform its dimensions properly, then "
                     "build the next process against those dimensions. Each star is usable the day "
                     "it lands, and the conforming work is spread rather than front-loaded.",
            },
        ],

        "cta_h": "See how many stars your database actually contains",
        "cta_p": "Netune classifies every table in a SQL Server database, finds the processes and "
                 "the dimensions they would share, and generates the conformed model with the bus "
                 "matrix filled in from the design.",
    },

    # ------------------------------------------------------------------ 6
    {
        "slug": "one-big-table.html",
        "short": "One Big Table",
        "oneline": "Everything joined in already; no joins to write",
        "crumb": "One Big Table",
        "thing": "Denormalized wide table",
        "title": "One Big Table (OBT): when a wide denormalised table beats a star schema",
        "short_title": "One Big Table (OBT)",
        "h1": "One Big Table: the wide denormalised model, and the bill it sends later",
        "meta": "When one wide table beats a star schema, what it costs in storage, correction and history, and the rule that stops OBT becoming one table holding everything.",
        "tw": "One wide table, no joins - fast to build, trivial to query, and expensive to correct.",
        "keywords": "one big table, OBT, wide table, denormalised table, OBT vs star schema, "
                    "flat table data warehouse, columnar, denormalization, single table analytics",
        "also": "OBT, the wide table, the flat table, full denormalisation",
        "standfirst": "The fastest model to build and the easiest to query, chosen honestly by "
                      "teams who know exactly what they are trading away &mdash; and chosen by "
                      "accident by teams who do not.",

        "what": [
            "One Big Table means exactly what it says: one wide table per subject, with every "
            "join already done. Customer name, product category, store region and the order line "
            "itself all sit on the same row, so the person asking the question never writes a "
            "join and never has to understand a key.",
            "It has a real following, and for good reasons. Columnar engines &mdash; BigQuery, "
            "Snowflake, Redshift, a clustered columnstore in SQL Server &mdash; only read the "
            "columns a query touches, so a table three hundred columns wide costs nothing extra "
            "for a query that reads four of them. Meanwhile the join that a star schema does at "
            "query time was done once, at load time.",
            "The critical word is <strong>per subject</strong>. One wide table for orders is a "
            "methodology. One wide table for the entire business is the thing people are picturing "
            "when they tell you OBT does not scale, and they are right about that one.",
        ],

        "shape": [
            {
                "h3": "What a row looks like",
                "code": "WideSales\n"
                        "  SalesKey             BIGINT\n"
                        "  OrderDate            DATE\n"
                        "  OrderNumber          NVARCHAR\n"
                        "  Quantity, LineTotal, UnitPrice\n"
                        "  -- everything below is repeated on every row of that customer's orders\n"
                        "  CustomerNumber, CustomerName, CustomerCity, CustomerSegment\n"
                        "  ProductCode, ProductName, SubcategoryName, CategoryName\n"
                        "  StoreCode, StoreName, RegionName",
                "after": [
                    "The load walks the source&rsquo;s foreign keys outward from the transaction "
                    "table, pulling each referenced table&rsquo;s columns in and naming them after "
                    "where they came from. It is a star schema with the joins resolved in advance "
                    "and the dimension tables thrown away.",
                ],
            },
            {
                "h3": "It is rebuilt, not updated",
                "body": [
                    "There is no incremental load worth the name and no history. The table is "
                    "cleared and rebuilt each run &mdash; truncate and reload &mdash; which is "
                    "the trade the methodology openly makes. A row is a snapshot of what "
                    "everything looked like when the load ran.",
                    "That also makes it safe to rebuild wholesale: nothing points at a wide table, "
                    "so there are no foreign keys to break and no surrogate keys anybody else is "
                    "holding.",
                ],
            },
            {
                "h3": "The one thing to record properly",
                "body": [
                    "Because every pulled-in column is named after the table it came from, it is "
                    "tempting to work out later where each one belongs by reading its name. A name "
                    "says which table a column came from; it never says what to join on. Record "
                    "the path &mdash; which table, through which key, in which order &mdash; when "
                    "the wide table is designed, or the next person rebuilding it is guessing.",
                ],
            },
        ],

        "fit_intro": "OBT is a genuinely good answer to a narrow question and a genuinely bad "
                     "answer to a broad one. The width of the question is the whole test.",
        "good_when": [
            "the tables are separate extracts that do not really relate",
            "few tables, or a single reporting need",
            "a small team that has to deliver something usable quickly",
            "the storage engine is columnar, where width costs little",
        ],
        "poor_when": [
            "a real star already exists in the source and would be thrown away",
            "the same customer or product detail must be corrected in one place",
            "history matters - a wide table has none",
            "many different reporting needs will pull the table in different directions",
        ],
        "cost": [
            ("Build", "Low",
             "The lowest of the eight. One table, one load, no keys to resolve."),
            ("Maintain", "High",
             "Every correction is a rewrite of many rows, and every new question widens the table."),
            ("Query", "Trivial",
             "No joins, no keys, no model to learn. This is the reason people choose it."),
            ("History", "None, unless you rebuild",
             "The table is a snapshot. Yesterday's version is gone unless you kept a copy."),
        ],

        "mistakes": [
            {
                "h3": "One table for everything, rather than one per process",
                "body": [
                    "The usual way this goes wrong. Sales, support tickets and inventory get "
                    "merged into one enormous table because they all mention customers, and now "
                    "every row has two thirds of its columns empty and nobody can say what one row "
                    "means. One wide table per business process; if two processes have different "
                    "grains, they are different tables.",
                ],
            },
            {
                "h3": "Correcting a customer’s name",
                "body": [
                    "In a star schema that is one row of one dimension. In a wide table it is "
                    "every row that customer ever appeared on &mdash; and if the table is rebuilt "
                    "from the source anyway, it is a source-system fix plus a full reload. Cheap "
                    "if the rebuild is nightly and routine; painful if the table took six hours to "
                    "build.",
                ],
            },
            {
                "h3": "Throwing away a star that was already there",
                "body": [
                    "If the source already has clean facts and dimensions, flattening them into a "
                    "wide table discards a model somebody already paid for, and buys query "
                    "simplicity that a BI tool would have hidden anyway. OBT earns its place where "
                    "the source is a pile of unrelated extracts, not where it is well modelled.",
                ],
            },
        ],

        "versus": [
            {
                "h3": "One Big Table or a star schema?",
                "body": [
                    "The trade is correction and history against joins. A "
                    "<a href=\"/kimball-dimensional-modeling.html\">star</a> lets you fix a "
                    "customer once and keep history per dimension, at the price of a join per "
                    "dimension &mdash; which every BI tool writes for you anyway. OBT removes the "
                    "joins and removes both of those abilities. For one process with a nightly "
                    "rebuild, OBT is defensible. For several processes sharing customers, the star "
                    "wins on almost every axis.",
                ],
            },
            {
                "h3": "One Big Table or Activity Schema?",
                "body": [
                    "Both are single-table models, and they answer opposite questions. OBT is wide "
                    "and holds one row per transaction with everything about it. "
                    "<a href=\"/activity-schema.html\">Activity Schema</a> is narrow and holds one "
                    "row per thing that happened, in sequence. If the questions are &ldquo;how "
                    "much, by whom&rdquo;, OBT. If they are &ldquo;what happened before "
                    "what&rdquo;, Activity Schema.",
                ],
            },
            {
                "h3": "Is OBT the same as a gold table in Medallion?",
                "body": [
                    "Often, in practice. Plenty of <a href=\"/medallion-architecture.html\">gold "
                    "layers</a> are wide denormalised tables, which means those teams have chosen "
                    "OBT as their model without naming it &mdash; and inherited its trade-offs "
                    "without discussing them.",
                ],
            },
        ],

        "netune_note": "Netune scores One Big Table on what it measures &mdash; how many separate "
                       "processes there are, whether real relationships exist, whether history "
                       "looks necessary &mdash; and warns rather than flatters when a wide table "
                       "would throw a usable star away. If you choose it, it generates the wide "
                       "table with the join path recorded properly.",

        "faq": [
            {
                "q": "Is One Big Table better than a star schema?",
                "a": "For one business process on a columnar engine, with a nightly rebuild and no "
                     "history requirement, it is simpler and just as fast. For several processes "
                     "sharing customers and products, or anywhere a detail must be corrected in "
                     "one place, a star schema is better on almost every axis.",
            },
            {
                "q": "Does OBT waste storage?",
                "a": "It repeats every descriptive value on every row, so yes in raw terms &mdash; "
                     "but columnar compression handles repeated values extremely well, and a "
                     "repeated string costs far less than it looks. On a row-store database the "
                     "cost is real.",
            },
            {
                "q": "How do I keep history in a wide table?",
                "a": "You do not, within the model. The usual answers are to keep dated snapshots "
                     "of the whole table, or to accept that history is not this model's job and "
                     "keep it upstream &mdash; which is a reason to look at a star schema or a "
                     "Data Vault instead.",
            },
            {
                "q": "How wide is too wide?",
                "a": "Width itself is rarely the problem on a columnar engine. The signal to watch "
                     "is emptiness: when most rows have most columns NULL, you have merged "
                     "processes with different grains into one table, and it should be two.",
            },
        ],

        "cta_h": "See whether a wide table would cost you a model",
        "cta_p": "Netune profiles a SQL Server database and says what shape is really in it "
                 "&mdash; including when the source already holds a usable star that flattening "
                 "would throw away.",
    },

    # ------------------------------------------------------------------ 7
    {
        "slug": "anchor-modeling.html",
        "short": "Anchor Modeling",
        "oneline": "One table per attribute; change never disturbs anything",
        "crumb": "Anchor Modeling",
        "thing": "Anchor modeling",
        "title": "Anchor Modeling explained: anchors, attributes, ties and knots (6NF)",
        "short_title": "Anchor Modeling",
        "h1": "Anchor Modeling: sixth normal form, and what one table per column really means",
        "meta": "Anchors, attributes, ties and knots - the 6NF model where adding anything never touches an existing table. What it buys, and what the join count costs.",
        "tw": "Anchors, attributes, ties and knots: everything cheap to change, everything expensive to read.",
        "keywords": "Anchor Modeling, 6NF, sixth normal form, anchors attributes ties knots, "
                    "temporal database, bitemporal, highly normalised data warehouse, "
                    "Anchor vs Data Vault",
        "also": "6NF modelling, anchors attributes ties and knots, the Anchor model",
        "standfirst": "The most rigorous model on this list, and the one whose costs are the most "
                      "immediate: everything it makes cheap to change, it makes expensive to read.",

        "what": [
            "Anchor Modeling stores data in the smallest pieces that can be stored separately. An "
            "<strong>anchor</strong> is an identity and nothing else &mdash; a surrogate key that "
            "says &ldquo;a customer exists&rdquo;. Every property of that customer is its own "
            "<strong>attribute</strong> table. Every relationship is its own <strong>tie</strong> "
            "table. Shared fixed vocabularies &mdash; a status list, a country list &mdash; are "
            "<strong>knots</strong>.",
            "The consequence is the headline: <strong>roughly one table per column</strong>. A "
            "customer with twenty properties becomes an anchor plus twenty attribute tables. That "
            "is not an exaggeration or a worst case; it is the design working as intended.",
            "What it buys is that change is always additive. A new property is a new table. "
            "Nothing that already exists is altered, no migration runs, nothing that was loaded "
            "has to move. And because each attribute carries its own validity time, you get "
            "complete history at attribute level for free &mdash; not &ldquo;this row changed&rdquo; "
            "but &ldquo;this customer&rsquo;s credit limit changed on this date, and nothing else "
            "did&rdquo;.",
        ],

        "shape": [
            {
                "h3": "The four constructs",
                "code": "CU_Customer            -- the anchor: an identity, nothing else\n"
                        "  CU_ID          INT\n"
                        "\n"
                        "CU_NAM_Customer_Name   -- one attribute = one table\n"
                        "  CU_ID          INT       -- which customer\n"
                        "  CU_NAM_Name    NVARCHAR  -- the value\n"
                        "  ChangedAt      DATETIME2 -- when it became true  (historised)\n"
                        "\n"
                        "CU_STA_Customer_Status -- a knotted attribute: value from a fixed list\n"
                        "  CU_ID, STA_ID, ChangedAt\n"
                        "\n"
                        "CU_pla_OR_Order_placed -- a tie: a relationship, its own table\n"
                        "  CU_ID, OR_ID",
            },
            {
                "h3": "The rule the whole model rests on",
                "body": [
                    "An anchor&rsquo;s surrogate key is assigned once and <strong>never "
                    "renumbered</strong>. Every attribute row and every end of every tie finds its "
                    "anchor by joining a natural key back through the anchor&rsquo;s identifying "
                    "attribute, so a second load has to arrive at the same number as the first. "
                    "Gaps in the sequence cost nothing; a number that moves costs everything "
                    "&mdash; the model quietly files one customer under two identities.",
                ],
            },
            {
                "h3": "History, and the trap in it",
                "body": [
                    "Every attribute read from one source row must be stamped with the same "
                    "moment, including the attribute whose value <em>is</em> a date. Reassembling "
                    "a readable row means joining the attributes on the anchor and that moment, so "
                    "one attribute stamping &ldquo;now&rdquo; while its neighbours stamp the order "
                    "date leaves nothing to join on.",
                    "A historised attribute also has to compare against the previous value "
                    "<em>within the same batch</em>, not only against what is already stored. "
                    "Checking only the stored value lets a first load write every reading it was "
                    "given, duplicates included, and call that a history.",
                ],
            },
            {
                "h3": "Nobody queries this by hand",
                "body": [
                    "Reassembling one customer means joining the anchor to every attribute table "
                    "you want, each filtered to the version that was current at the moment you "
                    "care about. Anchor Modeling&rsquo;s own answer is that the views are part of "
                    "the model &mdash; generated, not written &mdash; and that is the correct "
                    "answer. A model with no reporting layer planned is a model nobody can use.",
                ],
            },
        ],

        "fit_intro": "This one has the clearest fit test of the eight: who is going to write the "
                     "SQL, and how often will the model change?",
        "good_when": [
            "the model will keep changing and must never be rewritten",
            "history is needed per attribute, not per row",
            "the database engine can hide the joins behind views",
            "there is real appetite for a rigorous, academic approach",
        ],
        "poor_when": [
            "anyone will write SQL against it by hand",
            "the model is small or already stable",
            "the team is small - the table count grows quickly",
            "query performance matters more than flexibility",
        ],
        "cost": [
            ("Build", "High",
             "Many small tables, and the loads must agree about identity to the letter."),
            ("Maintain", "Low once built",
             "This is the payoff: adding anything is adding a table, never altering one."),
            ("Query", "Many joins",
             "One per attribute you want back. The generated views are not optional."),
            ("History", "Complete, per attribute",
             "The finest-grained history of the eight: every value, with when it became true."),
        ],

        "mistakes": [
            {
                "h3": "Building the model without building the views",
                "body": [
                    "The single most common way an Anchor project fails. The data is beautifully "
                    "stored and completely unreadable, and the team that has to report on it "
                    "writes twelve-join queries by hand until somebody proposes starting again. "
                    "The reporting views are part of the deliverable, at the same time as the "
                    "model, not afterwards.",
                ],
            },
            {
                "h3": "Letting the identifying attribute be cut off",
                "body": [
                    "The attribute that holds the natural key has to exist before anything else "
                    "can be loaded, because it is the only way back from a business key to the "
                    "surrogate. Build it first, whatever order the source lists its columns in "
                    "&mdash; a model whose identity attribute was left for later builds perfectly "
                    "and can never be filled.",
                ],
            },
            {
                "h3": "Choosing it for a stable, small model",
                "body": [
                    "Anchor&rsquo;s entire advantage is absorbing change without migration. On a "
                    "model that is not going to change much, you have paid the join cost and the "
                    "table count for a benefit that never arrives.",
                ],
            },
        ],

        "versus": [
            {
                "h3": "Anchor Modeling or Data Vault?",
                "body": [
                    "They solve the same problem with different granularity. A "
                    "<a href=\"/data-vault-2-0.html\">Data Vault</a> satellite holds a group of "
                    "attributes that change together; Anchor holds each one separately. That makes "
                    "Anchor&rsquo;s history finer and its join count higher. The vault also has "
                    "far more industry tooling, training and hiring pool around it, which for most "
                    "teams settles it.",
                ],
            },
            {
                "h3": "Anchor Modeling or a star schema?",
                "body": [
                    "Opposite ends of every trade. A "
                    "<a href=\"/kimball-dimensional-modeling.html\">star</a> is optimised for "
                    "being read and pays for it when the model changes; Anchor is optimised for "
                    "changing and pays for it every time it is read. Anywhere a real warehouse "
                    "uses Anchor, there is a dimensional layer on top of it.",
                ],
            },
        ],

        "netune_note": "Netune scores Anchor Modeling against the others and is deliberately blunt "
                       "about the table count when it does. If you choose it, it generates the "
                       "anchors, attributes, ties and knots in the order the keys require, with "
                       "one definition of how a natural key reaches a surrogate, and the mart "
                       "views that put the rows back together.",

        "faq": [
            {
                "q": "What are anchors, attributes, ties and knots?",
                "a": "An anchor is an identity and nothing else. An attribute is one property, in "
                     "its own table, usually with the moment it became true. A tie is one "
                     "relationship, also in its own table. A knot is a small fixed vocabulary "
                     "&mdash; a status or country list &mdash; shared across the model.",
            },
            {
                "q": "Is Anchor Modeling really one table per column?",
                "a": "Roughly, yes. That is the design rather than a symptom of it: because every "
                     "attribute is separate, adding one never touches an existing table and never "
                     "requires a migration. The cost is the join count, which is why the generated "
                     "views are part of the model.",
            },
            {
                "q": "What is 6NF, and is Anchor Modeling the same thing?",
                "a": "Sixth normal form decomposes tables until no non-trivial join dependency "
                     "remains &mdash; in practice, one attribute per table, which is what makes "
                     "temporal history natural. Anchor Modeling is a concrete methodology built on "
                     "6NF, with its own naming and its own generated views.",
            },
            {
                "q": "Is Anchor Modeling practical for a small team?",
                "a": "Rarely. The table count grows fast, the loads have to agree about identity "
                     "exactly, and the reporting views have to be generated rather than hand "
                     "written. It rewards a team with the tooling and the appetite for rigour, and "
                     "punishes one without.",
            },
        ],

        "cta_h": "See what Anchor would cost on your database",
        "cta_p": "Netune scores all eight methodologies against what it measures in a real SQL "
                 "Server database and shows the reasoning &mdash; including the table count an "
                 "Anchor model would actually produce from your schema.",
    },

    # ------------------------------------------------------------------ 8
    {
        "slug": "activity-schema.html",
        "short": "Activity Schema",
        "oneline": "One row per thing that happened, in sequence",
        "crumb": "Activity Schema",
        "thing": "Activity schema",
        "title": "Activity Schema: one table of events, and the questions it makes easy",
        "short_title": "Activity Schema",
        "h1": "Activity Schema: modelling what happened, in order, in one table",
        "meta": "The single-table event model: one row per thing that happened to one entity at one moment. What makes sequence questions cheap, and where it does not fit.",
        "tw": "One row per thing that happened - the model that makes 'what came before what' cheap.",
        "keywords": "activity schema, activity stream, event modelling, customer journey data "
                    "model, sequence analysis, temporal data model, activity schema vs star "
                    "schema, Narrator",
        "also": "the activity stream, event modelling, the customer timeline, the single-table event model",
        "standfirst": "The newest model on this list, and the only one built around the question "
                      "&ldquo;what happened next?&rdquo; rather than &ldquo;how much, by "
                      "whom?&rdquo;",

        "what": [
            "An Activity Schema is one table. Every row is one thing that happened to one entity "
            "at one moment: a customer signed up, placed an order, opened a ticket, cancelled. "
            "The entity is usually a customer; the moment is always required; everything else is "
            "detail hanging off those two.",
            "What that buys is sequence. &ldquo;What did people do between signing up and their "
            "first order?&rdquo;, &ldquo;how long until the second purchase?&rdquo;, &ldquo;what "
            "happened in the week before a cancellation?&rdquo; &mdash; these are ordinary reads "
            "of a single ordered table here, and awkward multi-table gymnastics in a star schema.",
            "It is a recent formalisation of something analytics teams kept building by hand, and "
            "it is deliberately narrow. It does not try to be a general warehouse model. It tries "
            "to make one family of questions cheap, and it succeeds.",
        ],

        "shape": [
            {
                "h3": "The stream",
                "code": "ActivityStream\n"
                        "  ActivityID           BIGINT IDENTITY\n"
                        "  EntityID             NVARCHAR   -- the customer, never NULL\n"
                        "  Activity             NVARCHAR   -- 'placed_order', 'opened_ticket'\n"
                        "  ActivityOccurredAt   DATETIME2  -- required; no time, no row\n"
                        "  ActivitySequence     INT        -- nth thing this entity did\n"
                        "  ActivityRepeatedAt   DATETIME2  -- next time THIS activity happened\n"
                        "  Feature1, Feature2, Feature3    -- meaning depends on the activity\n"
                        "  RevenueImpact        DECIMAL\n"
                        "  LinkID               NVARCHAR   -- back to the source row",
                "after": [
                    "The feature columns are the compromise that makes one table possible: their "
                    "meaning depends on which activity the row is. <code>Feature1</code> might be "
                    "a payment method on an order row and a ticket category on a support row.",
                ],
            },
            {
                "h3": "The two columns that are filled afterwards",
                "body": [
                    "<code>ActivitySequence</code> and <code>ActivityRepeatedAt</code> cannot be "
                    "computed while the rows are being inserted &mdash; both are window functions "
                    "over the <em>finished</em> stream. So the load has a second pass: insert "
                    "everything, then number each entity&rsquo;s activities in order and look "
                    "ahead to the next occurrence of the same activity for the same entity.",
                    "That second column is what makes &ldquo;how long between&rdquo; questions "
                    "cheap. Without it, every such question is a self-join over a large table.",
                ],
            },
            {
                "h3": "What the data has to have",
                "body": [
                    "Two requirements, and both are absolute. There must be <strong>one entity "
                    "everything relates to</strong> &mdash; usually a customer &mdash; and every "
                    "activity must carry <strong>a timestamp</strong>. An activity with no time "
                    "cannot be placed in a sequence, so it cannot be in the stream at all; leave "
                    "it out and say so, rather than defaulting it to the load time and corrupting "
                    "every ordering question.",
                    "Some activities reach the entity indirectly &mdash; an order line knows its "
                    "order, and the order knows the customer. Those hop through the parent, and "
                    "can inherit the parent&rsquo;s timestamp if they have none of their own. "
                    "Anything that can reach neither an entity nor a time is not an activity.",
                ],
            },
            {
                "h3": "The dictionary",
                "body": [
                    "Because the feature columns mean different things per activity, the model is "
                    "unreadable without a dictionary saying which is which. Keep it in the "
                    "warehouse as a real table, generated from the design &mdash; what an activity "
                    "means is a fact about the model, not about the source data &mdash; and it "
                    "stays accurate instead of rotting in a wiki.",
                ],
            },
        ],

        "fit_intro": "Activity Schema is the easiest of the eight to rule in or out, because its "
                     "requirements are concrete rather than a matter of judgement.",
        "good_when": [
            "the interesting questions are about what happened before or after something",
            "one entity - usually a customer - runs through everything",
            "the data is genuinely event-shaped, with timestamps everywhere",
            "the team is small and wants one table instead of a star",
        ],
        "poor_when": [
            "the data describes states rather than events",
            "there is no single entity that everything relates to",
            "few tables carry a timestamp",
            "the reporting is classic aggregation by category, not sequence",
        ],
        "cost": [
            ("Build", "Low to moderate",
             "One table, but one union arm per activity and a second pass after loading."),
            ("Maintain", "Low",
             "A new activity is a new arm of the union and a new dictionary row."),
            ("Query", "Easy for sequence",
             "And awkward for classic aggregation, which is the trade being made."),
            ("History", "Inherent - nothing is ever updated",
             "The stream is append-only: what happened, happened."),
        ],

        "mistakes": [
            {
                "h3": "Inventing a timestamp for an activity that has none",
                "body": [
                    "Defaulting a missing time to the load time puts the row in the stream at a "
                    "position that is not true, and every sequence and gap question involving that "
                    "entity is now quietly wrong. Leave the activity out and record why. An "
                    "untimed event is not an event.",
                ],
            },
            {
                "h3": "Letting the feature columns become undocumented",
                "body": [
                    "<code>Feature1</code> means five different things across five activities. "
                    "Without a maintained dictionary the table becomes unreadable within months, "
                    "and the people who knew have moved on. This is the model&rsquo;s main "
                    "maintenance obligation and it is not optional.",
                ],
            },
            {
                "h3": "Using it for state questions",
                "body": [
                    "&ldquo;How many customers are in Bavaria&rdquo; is a question about state, "
                    "and a stream of events answers it badly &mdash; you have to reconstruct the "
                    "current state by walking the history. If most of the reporting looks like "
                    "that, the questions are dimensional and the model should be too.",
                ],
            },
        ],

        "versus": [
            {
                "h3": "Activity Schema or a star schema?",
                "body": [
                    "Ask whether the questions are about state or about events. &ldquo;How much "
                    "did we sell, by region, last quarter&rdquo; is state and aggregation, and a "
                    "<a href=\"/kimball-dimensional-modeling.html\">star</a> answers it more "
                    "naturally. &ldquo;What did they do before they cancelled&rdquo; is sequence, "
                    "and a star makes you work hard for it. Plenty of organisations run both, "
                    "because both kinds of question are real.",
                ],
            },
            {
                "h3": "Activity Schema or One Big Table?",
                "body": [
                    "Both are one-table models. "
                    "<a href=\"/one-big-table.html\">OBT</a> is wide: one row per transaction with "
                    "everything about it attached. Activity Schema is narrow and long: one row per "
                    "thing that happened, ordered. Width answers &ldquo;how much&rdquo;; length "
                    "answers &ldquo;in what order&rdquo;.",
                ],
            },
            {
                "h3": "Activity Schema or Data Vault?",
                "body": [
                    "Both are append-only and keep everything. A "
                    "<a href=\"/data-vault-2-0.html\">vault</a> is an integration and audit layer "
                    "for many systems, structurally complex and not meant to be queried. An "
                    "Activity Schema is a reporting model for one entity&rsquo;s timeline, and is "
                    "meant to be queried directly. They are not really competing for the same job.",
                ],
            },
        ],

        "netune_note": "Netune checks the two things this model actually requires &mdash; whether "
                       "one entity runs through the database, and how many tables carry a usable "
                       "timestamp &mdash; before scoring it, and says plainly when the data is "
                       "state-shaped rather than event-shaped. If you build it, it generates the "
                       "stream, the second pass that fills the sequence columns, and the "
                       "dictionary.",

        "faq": [
            {
                "q": "What is an activity schema?",
                "a": "A single-table model where every row is one thing that happened to one "
                     "entity at one moment &mdash; a customer signed up, placed an order, "
                     "cancelled. It makes questions about sequence and timing cheap, because the "
                     "whole timeline is one ordered table.",
            },
            {
                "q": "How is an activity schema different from a fact table?",
                "a": "A fact table holds one kind of event at one grain, with typed columns for "
                     "that event. An activity stream holds every kind of event for an entity in "
                     "one table, with shared feature columns whose meaning depends on the "
                     "activity &mdash; which is what lets you read across activities in order.",
            },
            {
                "q": "What if some of my events have no timestamp?",
                "a": "They cannot be in the stream. An activity with no time cannot be sequenced, "
                     "and inventing one &mdash; defaulting to the load time, say &mdash; makes "
                     "every ordering question involving that entity wrong. Leave it out and record "
                     "why. If the activity has a parent with a time, it can inherit that.",
            },
            {
                "q": "Can I use an activity schema without a customer?",
                "a": "You need some single entity that everything relates to, but it does not have "
                     "to be a customer &mdash; a device, a vehicle, a shipment, an account all "
                     "work. What does not work is having no such entity: the stream has nothing "
                     "to be a timeline of.",
            },
        ],

        "cta_h": "See whether your data is event-shaped",
        "cta_p": "Netune measures how many of your tables carry timestamps, whether a single "
                 "entity runs through them, and whether the data describes events or states "
                 "&mdash; then scores this model against seven others on that evidence.",
    },
]
