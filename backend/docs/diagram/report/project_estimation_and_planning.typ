#align(center)[
= ANALISIS DESAIN SISTEM - Project Estimation
#table(
  align: left,
  columns: (auto, auto),
  [Kelompok], [3],
  [Tanggal Praktikum], [12 Mei 2026],
  [Paralel Praktikum], [3],
  [Waktu Praktikum], [10:00 - 12:00],
  [Anggota Kelompok], [
    - Ghaliyh Rayhan Adz-Dzikra (G6401231001)
    - Raihan Putra Kirana (G6401231027)
    - Insan Anshary Rasul (G6401231132)
  ],
)
]


== Kickoff Meeting

#table(
  columns: (auto, 1fr),
  [No], [Task List],
  [1], [Kickoff dan penyelarasan scope, tujuan, serta definisi sukses],
  [2], [Setup lingkungan dev dan struktur repo (backend, frontend, tooling)],
  [3], [Baseline database, migrasi, dan seed data awal untuk semua role],
  [4], [Implementasi auth, JWT, refresh token, dan RBAC],
  [5], [Profile management dan master data (departments, skills, companies)],
  [6], [Job board dan vacancy management (admin CRUD, search, filter)],
  [7], [Wishlist dan job matching berbasis skill],
  [8], [Application tracking dan self-reported ATS dengan audit log],
  [9], [Placement activation dan daily activity log],
  [10], [Auto report generation dan document request (PDF)],
  [11], [Notification system (in-app, unread, read/delete)],
  [12], [Frontend UI dan integrasi API per phase (auth, profile, job board, aplikasi)],
  [13], [Dashboard dan analytics (student dan admin)],
  [14], [Testing dan QA (unit, integration, e2e, test gate per phase)],
  [15], [CI/CD, deployment pipeline, dan environment staging/production],
  [16], [Monitoring, logging, dan hardening security],
  [17], [Data prefill dan skenario uji untuk validasi UI/flow],
  [18], [UX polish, aksesibilitas, dan konsistensi design system],
  [19], [Performance tuning (query optimization, caching, pagination)],
  [20], [UAT, rilis bertahap, dan handover dokumentasi],
)

== Individual Preparation

=== Role: Front-end Dev (Ghaliyh Rayhan Adz-Dzikra - G6401231001)

#table(
  columns: (1fr, auto, 1fr),
  [*Task List*], [*Time (days)*], [*Assumption*],
  [Frontend foundation: routing, query provider, env config], [2], [Struktur repo dan guideline UI sudah disepakati],
  [Auth UI integration (login, register, verify, forgot)], [3], [Endpoint auth backend stabil],
  [Profile UI + master data dropdown], [3], [Endpoint profile dan departments siap],
  [Job board listing + filter + detail], [4], [Vacancy list/detail tersedia dan konsisten],
  [Wishlist + match indicator], [2], [Endpoint wishlist dan match tersedia],
  [Application tracking UI + status update], [4], [Endpoint application dan history siap],
  [Placement + jurnal harian UI], [3], [Endpoint placement dan activity log siap],
  [Report + document request UI], [3], [Endpoint report dan document siap],
  [Dashboard + analytics + notification center], [3], [Endpoint analytics dan notification siap],
  [UX polish + aksesibilitas + responsive], [2], [Design system sudah final],
  [Integrasi testing + bugfix], [3], [Data prefill dan test env tersedia],
)

=== Role: Project Lead (Raihan Putra Kirana - G6401231027)

#table(
  columns: (1fr, auto, 1fr),
  [*Task List*], [*Time (days)*], [*Assumption*],
  [Scope breakdown, milestone, dan risk register], [2], [Stakeholder tersedia untuk alignment awal],
  [API contract dan data model alignment lintas tim], [2], [Roadmap backend dan frontend stabil],
  [Backend auth + RBAC + user management], [4], [DB schema sudah siap],
  [Backend profile + master data CRUD], [4], [Migration baseline sudah jalan],
  [Backend vacancy CRUD + search/filter], [4], [Seed data dan indexing siap],
  [Dokumentasi API dan contoh payload], [2], [Endpoint utama sudah ditentukan],
  [Koordinasi integrasi FE auth/profile + bugfix], [3], [FE foundation selesai],
  [Dashboard/analytics initial integration], [3], [Analytics endpoint tersedia],
  [Code review, QA gate, dan release checklist], [3], [Test plan disepakati],
  [CI/CD pipeline + env staging/production], [3], [Akses infra tersedia],
  [Demo stakeholder + loop UAT], [2], [Jadwal stakeholder tersedia],
)

=== Role: Back-end Dev (Insan Anshary Rasul - G6401231132)

#table(
  columns: (1fr, auto, 1fr),
  [*Task List*], [*Time (days)*], [*Assumption*],
  [Application tracking + status transition rules], [4], [Auth dan vacancy sudah siap],
  [Audit log/history otomatis], [3], [Trigger atau event listener disepakati],
  [Proof upload (storage + validation)], [2], [Object storage siap],
  [Admin verification + placement activation], [3], [Admin endpoints tersedia],
  [Placement + activity log CRUD], [4], [Schema placement stabil],
  [Auto report generation (PDF)], [5], [Template laporan final],
  [Document request + cover letter generator], [4], [Template surat final],
  [Notification system backend], [3], [Event trigger didefinisikan],
  [Test suite phase 4-6], [4], [Test env dan seed data tersedia],
  [Performance tuning + cleanup], [2], [Baseline metrics tersedia],
)

== Estimation Session

=== Role: Front-end Dev (Ghaliyh Rayhan Adz-Dzikra - G6401231001)

#table(
  columns: (1fr, auto, auto, auto, auto),
  [*Task*], [*Initiate Estimate (days)*], [*Change 1*], [*Change 2*], [*Final*],
  [Frontend foundation: routing, query provider, env config], [2], [1], [0], [3],
  [Auth UI integration (login, register, verify, forgot)], [3], [1], [0], [4],
  [Profile UI + master data dropdown], [3], [1], [0], [4],
  [Job board listing + filter + detail], [4], [2], [-1], [5],
  [Wishlist + match indicator], [2], [1], [0], [3],
  [Application tracking UI + status update], [4], [2], [-1], [5],
  [Placement + jurnal harian UI], [3], [1], [0], [4],
  [Report + document request UI], [3], [1], [-1], [3],
  [Dashboard + analytics + notification center], [3], [1], [-1], [3],
  [UX polish + aksesibilitas + responsive], [2], [1], [0], [3],
  [Integrasi testing + bugfix], [3], [1], [-1], [3],
  [Net change], [], [13], [-5], [8],
  [Total], [32], [45], [40], [40],
)

=== Role: Project Lead (Raihan Putra Kirana - G6401231027)

#table(
  columns: (1fr, auto, auto, auto, auto),
  [*Task*], [*Initiate Estimate (days)*], [*Change 1*], [*Change 2*], [*Final*],
  [Scope breakdown, milestone, dan risk register], [2], [1], [0], [3],
  [API contract dan data model alignment lintas tim], [2], [1], [0], [3],
  [Backend auth + RBAC + user management], [4], [1], [-1], [4],
  [Backend profile + master data CRUD], [4], [1], [0], [5],
  [Backend vacancy CRUD + search/filter], [4], [2], [-1], [5],
  [Dokumentasi API dan contoh payload], [2], [1], [0], [3],
  [Koordinasi integrasi FE auth/profile + bugfix], [3], [1], [0], [4],
  [Dashboard/analytics initial integration], [3], [1], [-1], [3],
  [Code review, QA gate, dan release checklist], [3], [1], [-1], [3],
  [CI/CD pipeline + env staging/production], [3], [1], [0], [4],
  [Demo stakeholder + loop UAT], [2], [1], [0], [3],
  [Net change], [], [12], [-4], [8],
  [Total], [32], [44], [40], [40],
)

=== Role: Back-end Dev (Insan Anshary Rasul - G6401231132)

#table(
  columns: (1fr, auto, auto, auto, auto),
  [*Task*], [*Initiate Estimate (days)*], [*Change 1*], [*Change 2*], [*Final*],
  [Application tracking + status transition rules], [4], [1], [-1], [4],
  [Audit log/history otomatis], [3], [1], [0], [4],
  [Proof upload (storage + validation)], [2], [1], [0], [3],
  [Admin verification + placement activation], [3], [1], [0], [4],
  [Placement + activity log CRUD], [4], [1], [0], [5],
  [Auto report generation (PDF)], [5], [2], [-2], [5],
  [Document request + cover letter generator], [4], [1], [-1], [4],
  [Notification system backend], [3], [1], [0], [4],
  [Test suite phase 4-6], [4], [1], [-1], [4],
  [Performance tuning + cleanup], [2], [1], [0], [3],
  [Net change], [], [11], [-5], [6],
  [Total], [34], [45], [40], [40],
)

== Assemble Session

#table(
  columns: (auto, 1fr, auto, auto, auto, auto, auto, auto),
  [*WBS*], [*Task name*], [*Ghaliyh*], [*Raihan*], [*Insan*], [*Best case*], [*Worst case*], [*Avg (hi & lo)*],
  [1], [Kickoff dan penyelarasan scope, tujuan, serta definisi sukses], [1], [2], [1], [1], [2], [1.33],
  [2], [Setup lingkungan dev dan struktur repo (backend, frontend, tooling)], [2], [3], [2], [2], [3], [2.33],
  [3], [Baseline database, migrasi, dan seed data awal untuk semua role], [1], [3], [4], [1], [4], [2.67],
  [4], [Implementasi auth, JWT, refresh token, dan RBAC], [2], [4], [3], [2], [4], [3.00],
  [5], [Profile management dan master data (departments, skills, companies)], [3], [4], [3], [3], [4], [3.33],
  [6], [Job board dan vacancy management (admin CRUD, search, filter)], [4], [4], [3], [3], [4], [3.67],
  [7], [Wishlist dan job matching berbasis skill], [2], [3], [3], [2], [3], [2.67],
  [8], [Application tracking dan self-reported ATS dengan audit log], [3], [3], [4], [3], [4], [3.33],
  [9], [Placement activation dan daily activity log], [3], [3], [4], [3], [4], [3.33],
  [10], [Auto report generation dan document request (PDF)], [3], [3], [5], [3], [5], [3.67],
  [11], [Notification system (in-app, unread, read/delete)], [2], [3], [3], [2], [3], [2.67],
  [12], [Frontend UI dan integrasi API per phase (auth, profile, job board, aplikasi)], [5], [4], [2], [2], [5], [3.67],
  [13], [Dashboard dan analytics (student dan admin)], [3], [3], [2], [2], [3], [2.67],
  [14], [Testing dan QA (unit, integration, e2e, test gate per phase)], [2], [3], [3], [2], [3], [2.67],
  [15], [CI/CD, deployment pipeline, dan environment staging/production], [1], [3], [2], [1], [3], [2.00],
  [16], [Monitoring, logging, dan hardening security], [1], [2], [3], [1], [3], [2.00],
  [17], [Data prefill dan skenario uji untuk validasi UI/flow], [2], [2], [3], [2], [3], [2.33],
  [18], [UX polish, aksesibilitas, dan konsistensi design system], [3], [2], [1], [1], [3], [2.00],
  [19], [Performance tuning (query optimization, caching, pagination)], [2], [3], [3], [2], [3], [2.67],
  [20], [UAT, rilis bertahap, dan handover dokumentasi], [2], [3], [2], [2], [3], [2.33],
)

== Task Scheduling

#table(
  columns: (auto, 1fr, auto),
  [No], [Task], [Predecessor],
  [1], [Kickoff dan penyelarasan scope, tujuan, serta definisi sukses], [-],
  [2], [Setup lingkungan dev dan struktur repo (backend, frontend, tooling)], [1],
  [3], [Baseline database, migrasi, dan seed data awal untuk semua role], [2],
  [4], [Implementasi auth, JWT, refresh token, dan RBAC], [3],
  [5], [Profile management dan master data (departments, skills, companies)], [4],
  [6], [Job board dan vacancy management (admin CRUD, search, filter)], [5],
  [7], [Wishlist dan job matching berbasis skill], [6],
  [8], [Application tracking dan self-reported ATS dengan audit log], [6],
  [9], [Placement activation dan daily activity log], [8],
  [10], [Auto report generation dan document request (PDF)], [9],
  [11], [Notification system (in-app, unread, read/delete)], [4],
  [12], [Frontend UI dan integrasi API per phase (auth, profile, job board, aplikasi)], [4, 5, 6, 7, 8],
  [13], [Dashboard dan analytics (student dan admin)], [12],
  [14], [Testing dan QA (unit, integration, e2e, test gate per phase)], [10, 11, 13, 17],
  [15], [CI/CD, deployment pipeline, dan environment staging/production], [2],
  [16], [Monitoring, logging, dan hardening security], [15],
  [17], [Data prefill dan skenario uji untuk validasi UI/flow], [3],
  [18], [UX polish, aksesibilitas, dan konsistensi design system], [12],
  [19], [Performance tuning (query optimization, caching, pagination)], [6, 8, 9],
  [20], [UAT, rilis bertahap, dan handover dokumentasi], [14, 16, 18, 19],
)


#pagebreak()
#set page(flipped: true)
== Gantt Chart

#{
  import "@preview/gantty:0.5.1" as gantty
  import gantty: gantt
  import gantty.task: default-tasks-drawer
  import gantty.sidebar: default-sidebar-drawer
  import gantty.field: default-field-drawer
  import gantty.header: default-headers-drawer
  import gantty.dividers: default-dividers-drawer
  import gantty.dependencies: orthogonal-dependencies-drawer
  import gantty.milestones: default-milestones-drawer

  let drawer = (
    sidebar: default-sidebar-drawer.with(spacing: 6pt),
    field: default-field-drawer,
    headers: default-headers-drawer,
    dividers: default-dividers-drawer.with(styles: (none,)),
    tasks: default-tasks-drawer.with(
      styles: (
        (
          uncompleted: (style: (fill: rgb("#4C78A8")), width: 10pt),
          completed-early: (
            timeframe: (style: (fill: rgb("#72B7B2")), width: 10pt),
            body: (style: (fill: rgb("#4C78A8")), width: 10pt),
          ),
          completed-late: (
            timeframe: (style: (fill: rgb("#F58518")), width: 10pt),
            body: (style: (fill: rgb("#4C78A8")), width: 10pt),
          ),
        ),
      ),
    ),
    dependencies: orthogonal-dependencies-drawer.with(style: (
      stroke: luma(10%) + 0.8pt,
      radius: 8pt,
      mark: (end: "straight"),
    )),
    milestones: default-milestones-drawer,
  )

  let gantt = gantt.with(drawer: drawer)
  gantt(yaml("gantt.yaml"))
}


#pagebreak()
#set page(flipped: true)
== Critical Path (PERT)

#{
  import "@preview/fletcher:0.5.8": diagram, edge, node

  let crit = rgb("#E45756")
  let normal = rgb("#4C78A8")
  let fill-normal = rgb("#E8F1FA")
  let fill-critical = rgb("#FADBD8")

  let task = (pos, label, name, critical: false) => node(
    pos,
    label,
    name: name,
    radius: 1.2em,
    fill: if critical { fill-critical } else { fill-normal },
  )

  diagram(
    cell-size: 12mm,
    spacing: (8mm, 6mm),
    node-stroke: 0.8pt + luma(30%),
    edge-stroke: 0.7pt + luma(40%),
    {
      node((0, 2), [Start], name: <start>, corner-radius: 2pt, fill: fill-normal)

      task((1, 2), align(center)[1\ (2d)], <t1>, critical: true)
      task((2, 2), align(center)[2\ (10d)], <t2>, critical: true)
      task((3, 2), align(center)[3\ (14d)], <t3>, critical: true)
      task((4, 2), align(center)[4\ (13d)], <t4>, critical: true)
      task((5, 2), align(center)[5\ (14d)], <t5>, critical: true)
      task((6, 2), align(center)[6\ (15d)], <t6>, critical: true)

      task((7, 1), align(center)[7\ (7d)], <t7>)
      task((7, 2), align(center)[8\ (14d)], <t8>, critical: true)
      task((7, 3), align(center)[11\ (8d)], <t11>)

      task((8, 2), align(center)[9\ (10d)], <t9>)
      task((9, 2), align(center)[10\ (13d)], <t10>)
      task((10, 3), align(center)[19\ (11d)], <t19>)

      task((8, 1), align(center)[12\ (33d)], <t12>, critical: true)
      task((9, 1), align(center)[13\ (7d)], <t13>, critical: true)
      task((10, 1), align(center)[14\ (11d)], <t14>, critical: true)

      task((3, 4), align(center)[15\ (14d)], <t15>)
      task((4, 4), align(center)[16\ (14d)], <t16>)
      task((4, 5), align(center)[17\ (8d)], <t17>)
      task((9, 3), align(center)[18\ (11d)], <t18>)

      task((11, 2), align(center)[20\ (5d)], <t20>, critical: true)
      node((12, 2), [Finish], name: <finish>, corner-radius: 2pt, fill: fill-normal)

      edge(<start>, <t1>, "-|>", stroke: crit + 1.2pt)
      edge(<t1>, <t2>, "-|>", stroke: crit + 1.2pt)
      edge(<t2>, <t3>, "-|>", stroke: crit + 1.2pt)
      edge(<t3>, <t4>, "-|>", stroke: crit + 1.2pt)
      edge(<t4>, <t5>, "-|>", stroke: crit + 1.2pt)
      edge(<t5>, <t6>, "-|>", stroke: crit + 1.2pt)

      edge(<t6>, <t7>, "-|>")
      edge(<t6>, <t8>, "-|>", stroke: crit + 1.2pt)
      edge(<t4>, <t11>, "-|>")

      edge(<t8>, <t9>, "-|>")
      edge(<t9>, <t10>, "-|>")
      edge(<t9>, <t19>, "-|>")

      edge(<t7>, <t12>, "-|>")
      edge(<t8>, <t12>, "-|>", stroke: crit + 1.2pt)

      edge(<t12>, <t13>, "-|>", stroke: crit + 1.2pt)
      edge(<t13>, <t14>, "-|>", stroke: crit + 1.2pt)
      edge(<t17>, <t14>, "-|>")
      edge(<t10>, <t14>, "-|>")
      edge(<t11>, <t14>, "-|>")

      edge(<t2>, <t15>, "-|>")
      edge(<t15>, <t16>, "-|>")
      edge(<t3>, <t17>, "-|>")
      edge(<t12>, <t18>, "-|>")

      edge(<t14>, <t20>, "-|>", stroke: crit + 1.2pt)
      edge(<t16>, <t20>, "-|>")
      edge(<t18>, <t20>, "-|>")
      edge(<t19>, <t20>, "-|>")
      edge(<t20>, <finish>, "-|>", stroke: crit + 1.2pt)
    },
  )
}

#pagebreak()
#set page(flipped: false)

== Penjelasan Critical Path

Durasi PERT diambil dari rentang tanggal pada Gantt (durasi inklusif). Jalur kritis adalah rangkaian task dengan slack $0$ sehingga menentukan durasi total proyek.

Task critical:

- 1 Kickoff dan penyelarasan scope
- 2 Setup lingkungan dev dan struktur repo
- 3 Baseline database dan migrasi
- 4 Implementasi auth dan RBAC
- 5 Profile management dan master data
- 6 Job board dan vacancy management
- 8 Application tracking (ATS)
- 12 Frontend integrasi API per phase
- 13 Dashboard dan analytics
- 14 Testing dan QA
- 20 UAT, rilis, dan handover

Makna:

- Task di critical path tidak memiliki buffer; jika terlambat, jadwal proyek ikut bergeser.
- Task di luar critical path memiliki buffer (slack); keterlambatan selama masih dalam buffer tidak mengubah tanggal selesai proyek.

Task dengan buffer (slack, hari):

#table(
  columns: (1fr, auto),
  [Task], [Buffer (days)],
  [7 Wishlist dan job matching], [7],
  [9 Placement dan activity log], [30],
  [10 Auto report dan document request], [33],
  [11 Notification system], [39],
  [15 CI/CD dan staging], [93],
  [16 Monitoring dan hardening security], [93],
  [17 Data prefill untuk validasi UI], [88],
  [18 UX polish dan aksesibilitas], [7],
  [19 Performance tuning], [30],
)



