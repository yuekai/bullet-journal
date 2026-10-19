---
title: Tailnet
description: Tailnet policy and admin notes
date: 2026-10-18
---

Tailnet: `taildd337d.ts.net`. This machine (`mbp`) is the tailnet owner and
admin.

## Policy file

This section holds the policy snapshot from 2026-10-18. The admin console is
the authority. Fetch the current policy before each edit.

```json
{
	"tagOwners": {
		"tag:llama-gateway": [
			"autogroup:admin"
		],
		"tag:comet-gateway": [
			"autogroup:admin"
		],
		"tag:comet-client": [
			"autogroup:admin"
		]
	},

	// Users keep full tailnet access. Tagged devices are not members, and no
	// grant has tag:llama-gateway or tag:comet-gateway as src, so gateway
	// machines are inbound-only: they accept connections to their service
	// (return traffic on allowed connections passes statefully) but cannot
	// initiate connections to anything else on the tailnet.
	"grants": [
		{
			"src": [
				"autogroup:member"
			],
			"dst": [
				"*"
			],
			"ip": [
				"*"
			]
		},
		// llama is members-only by design: sole user, so deliberately no
		// client tag and no client grant.
		{
			"src": [
				"autogroup:member"
			],
			"dst": [
				"svc:llama"
			],
			"ip": [
				"8000",
				"58627",
				"3080",
				"3081"
			]
		},
		{
			"src": [
				"autogroup:member"
			],
			"dst": [
				"svc:comet"
			],
			"ip": [
				"8000",
				"8088"
			]
		},
		// comet clients can reach the comet service and, by deny-by-default,
		// nothing else on the tailnet.
		{
			"src": [
				"tag:comet-client"
			],
			"dst": [
				"svc:comet"
			],
			"ip": [
				"8000",
				"8088"
			]
		}
	],

	"autoApprovers": {
		"services": {
			"svc:llama": [
				"tag:llama-gateway"
			],
			"svc:comet": [
				"tag:comet-gateway"
			]
		}
	},

	// Test access rules every time they're saved.
	"tests": [
		{
			// Keep plain SSH to spark from regressing during future policy edits.
			"src":   "yuekai@gmail.com",
			"proto": "tcp",
			"accept": [
				"100.91.181.87:22"
			]
		},
		{
			// Members can reach the DSH web UI and its gate on spark.
			"src":   "yuekai@gmail.com",
			"proto": "tcp",
			"accept": [
				"100.91.181.87:3080",
				"100.91.181.87:3081"
			]
		},
		{
			// Members can reach the llama service.
			"src":   "yuekai@gmail.com",
			"proto": "tcp",
			"accept": [
				"svc:llama:8000",
				"svc:llama:58627",
				"svc:llama:3080",
				"svc:llama:3081"
			]
		},
		{
			// The llama gateway must not initiate connections to other machines.
			"src":   "tag:llama-gateway",
			"proto": "tcp",
			"deny": [
				"100.91.181.87:22"
			]
		},
		{
			// Members can reach the comet service.
			"src":   "yuekai@gmail.com",
			"proto": "tcp",
			"accept": [
				"svc:comet:8000",
				"svc:comet:8088"
			]
		},
		{
			// The comet gateway must not initiate connections to other machines.
			"src":   "tag:comet-gateway",
			"proto": "tcp",
			"deny": [
				"100.91.181.87:22"
			]
		},
		{
			// comet clients can reach the comet service...
			"src":   "tag:comet-client",
			"proto": "tcp",
			"accept": [
				"svc:comet:8000",
				"svc:comet:8088"
			]
		},
		{
			// ...and nothing else.
			"src":   "tag:comet-client",
			"proto": "tcp",
			"deny": [
				"100.91.181.87:22"
			]
		}
	]
}
```

## What the policy does

- A member has full access to each machine on the tailnet. The rule is
  `autogroup:member` to `*`.
- A gateway machine is inbound-only. The tag is `tag:llama-gateway` or
  `tag:comet-gateway`. The machine accepts connections to its service. The
  machine cannot start a connection to another machine. No grant has either
  tag as `src`, so the default denies the start.
- The tag approves the service advertisement. The rule is in
  `autoApprovers.services`.
- A `tag:comet-client` machine can reach `svc:comet` on port 8000 and port
  8088 only. The default denies each other connection. The default also
  denies SSH and peer-to-peer traffic.
- `svc:llama` is for members only. The tailnet has one user, so there is no
  client tag and no client grant. The member grant holds tcp:8000, tcp:58627,
  tcp:3080, and tcp:3081. Port 3081 is the permanent bookmark port of the
  llama DSH gate.
- The `tests` section guards SSH access to `spark` at `100.91.181.87:22`. A
  member must keep this access. A gateway machine and a client machine must
  never get it.
- `spark` has no service and no tag. Its own `tailscaled` serves the DSH web
  UI on tcp:3080 and the DSH gate on tcp:3081. The member grant to `*` covers
  both ports. A test pins `100.91.181.87:3080` and `100.91.181.87:3081` for a
  member. See [dsh-on-spark.md](dsh-on-spark.md).
- The `tests` section also guards each service. A client accepts its service
  and nothing else. A gateway cannot start a connection. A member accepts
  `svc:llama` on all four ports, and `svc:comet` on port 8000 and port 8088.

## Admin notes for agent use

**Read the policy.** Run this command:

```bash
set -a; . ~/.env; set +a
curl -u "$TS_API_KEY:" https://api.tailscale.com/api/v2/tailnet/-/acl
```

`TS_API_KEY` comes from `~/.env`. A non-login shell does not inherit this
variable. Load the file first, or the command sends an empty credential. The
answer is HuJSON. Comments and trailing commas are permitted.

**Update the policy.** Do these steps in order:

1. Run the read command and keep the `ETag` response header.
2. Edit the policy.
3. Send the file back with the `If-Match` header and the `ETag` value. This
   header stops a change to a policy that another person edited.
4. Use `--data-binary @file` in the POST. The option `-d` removes newlines and
   breaks the HuJSON comments.
5. Keep the `tests` section correct. The API refuses a save that breaks a
   test.

**Add an access rule.** Write a grant. A grant is the recommended form in
Tailscale. Read the old `acls` section only to read an old policy. The
sections `ssh`, `autoApprovers`, `nodeAttrs`, `postures`, `groups`, and
`tagOwners` have their own syntax.

**Reference.** The full API reference is in
`~/.agents/skills/tailscale/references/api.md`. The access-control reference
is in `~/.agents/skills/tailscale/references/access-control.md`.

## Policy history

- 2026-09-10: The admin console removed the sglang and kimi services and their
  tags. The tags were `tag:sglang-relay`, `tag:sglang-client`, and
  `tag:kimi-router`.
- 2026-09-10: The admin console added `svc:llama` with `tag:llama-gateway`,
  and `svc:comet` with `tag:comet-gateway`.
- 2026-09-14: The admin console added `tag:comet-client`. The grant and the
  tests limited that tag to `svc:comet:8000`.
- 2026-09-21: The admin console removed the vLLM service and the tags
  `tag:vllm-relay` and `tag:vllm-client`. No `svc:vllm` grant, no vllm tag
  owner, and no vllm test remain.
- 2026-09-21: `svc:llama` gained tcp:3081. `svc:comet` gained tcp:8088. This
  note now matches the policy from the API.
- 2026-10-18: The API renamed the machine `dgx-spark` to `spark` and disabled
  its key expiry. The policy gained a member test for `100.91.181.87:3080` and
  `100.91.181.87:3081`, the spark DSH ports. The live policy has no comments.
  The comments in the snapshot above exist only in this note.
- 2026-10-19: The API renamed the machines `syk-ipad` to `ipad`, `syk-iphone`
  to `iphone`, `syk-legionp` to `legionp`, and `syk-mbp` to `mbp`, and
  disabled key expiry on each. Every machine on the tailnet now has key
  expiry disabled.
