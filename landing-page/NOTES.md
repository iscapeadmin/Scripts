# iScape landing page: build notes (taste-skill run)

Reading of the brief: a landing page for iScape, a managed IT provider in Mackay, Queensland,
aimed at local small and medium businesses. One action: book an IT review.

## Inventory (things that belong to iScape and Mackay, not to every MSP)
1. iScape Pty Ltd, North Mackay, Qld 4740 (directory listing: 8 Evans Avenue). **Confirm.**
2. Founded 2005 (Peter Everitt and Stewart McKinnon); joined with Veltech Computer Services in 2008. **Confirm.**
3. Mackay: Australia's sugar capital. Cane fields, sugar mills crushing June to November, steam over the mill stack.
4. Narrow-gauge cane trains and their bins running through the district during the crush.
5. Coal: the Bowen Basin inland (Moranbah) and the Hay Point coal terminal south of town.
6. The coast: the Pioneer River mouth, Whitsunday islands to the north.
7. Cyclone season, 1 November to 30 April: power and NBN outages, closed offices, scam emails after storms.
8. Rural sites on Starlink or 4G, because the NBN doesn't reach every shed.
9. Today is 22 October: ten days to the start of the season.

## Argument (one claim per section, with its proof)
- hero: iScape is Mackay's IT, ready before cyclone season → the district drawn large, the storm in the headline.
- intro: Mackay runs on cane, coal and the coast; iScape keeps the offices behind them working → three inline pictures.
- features: what's looked after: helpdesk, backups, security, connections → four rows with drawings.
- how-it-works: how you start, in four plain steps → the staircase.
- check (live): you can find out right now whether you're ready for 1 November → five questions, the answer, the button.
- showcase: local, from the Basin to Evans Avenue → one map at three distances.
- about: who iScape is and since when → the paragraph with the cane loco as a drop cap.
- faq: the real objections answered → six questions.
- contact: write to us → the email address as display type.
- footer: invitation, cropped name.

## Idea
On this page, **Mackay's cyclone season** becomes **the picture inside the sentence**: a looping
satellite swirl sits in the headline where the word "cyclone" would be, and the season's start date
drives the one live thing.

Competitor test: another Mackay MSP could borrow "cyclone season", so the idea is carried by what's
only iScape's: North Mackay since 2005, the district map down to Evans Avenue, and the countdown and
check built around the real season dates.

Live thing: the cyclone-season check. A countdown to 1 November (or the day of the season, once it
starts), five yes/no questions about the office, a verdict that updates, and "Book a review" pre-filled
with the answers as an email. Plain form without script.

## Copy deck
Nav: iScape · Services · Cyclone check · About · FAQ · [Book a review]

H1: Mackay IT, ready / for [cyclone] season
Support (split on the horizon): "Managed IT for Mackay businesses since 2005" | "helpdesk, backups, security and connections, looked after from North Mackay."

Intro (p): Mackay runs on [cane] cane, [coal] coal and the [coast] coast. Since 2005, iScape has kept the offices behind them working: the computers, the email, the backups and the connections.

Features H2: What we look after
1. A helpdesk in Mackay: call and talk to a technician who knows your office, and who can be at your door the same day when a fix needs hands.
2. Backups that leave town: every night your files are copied to data centres well outside the cyclone zone, and we test restoring them, not just that the job ran.
3. Security to the Essential Eight: multi-factor sign-in, patching and email filtering set to the Australian Cyber Security Centre's Essential Eight, because the scam emails arrive with the storms.
4. Connections that hold: NBN with automatic 4G or 5G failover, Starlink for the farm and the site office, and a UPS so a flicker doesn't take the server with it.

How it works (staircase, the first line is the heading):
- First we walk your site. An hour at your office or shed: every computer, the modem, the backups, and who signs in to what.
- Then we write it down. A plain-English report: what's there, what's at risk, and what fixing it would cost.
- We fix the urgent things. Usually backups, multi-factor sign-in and the tired router, in the first fortnight.
- Then it's ours to watch. Monitoring, updates and the helpdesk from then on, for a fixed monthly fee.

Check H2: Ready by 1 November?
Countdown line: "10 days until cyclone season" / "Cyclone season: day N of 181"
Questions:
1. Are your backups copied somewhere outside Mackay?
2. Could your team work from home tomorrow if the office shut?
3. Are the server, modem and phones on a UPS?
4. Is there a mobile backup if the NBN drops?
5. Does everyone sign in with multi-factor authentication?
Verdict by count: 5 "Ready. We'd still test the restore." / 3-4 "Close. N things to fix before the first watch." / 0-2 "Not yet. Let's fix it before November."
Button: Book a review (mailto with answers)

Showcase H2 halves: "From the Basin" / "to Evans Avenue"
Caption: On site from Airlie Beach to Sarina and out to Moranbah; remote support anywhere. The office is in North Mackay, north of the river.

About (p, drop cap: drawn cane loco): iScape was started in Mackay in 2005 by Peter Everitt and Stewart McKinnon, and joined with Veltech Computer Services in 2008. ... Facts: North Mackay, Qld / Since 2005 / Book a review.

FAQ H2: Questions we get asked (six)
Contact: hello@iscape.com.au (SAMPLE, confirm), sentence: "Tell us about the office, the shed, or the one computer that keeps beeping."
Footer: "Get ready / before November" + Book a review; links; cropped "iScape".

## Sample content to confirm before launch
Email address, street address, founders and merger history, service area, the 4-step onboarding,
the backup locations, fixed monthly fee, FAQ answers.

## Critique (taste-skill references/critique.md §4)

ROUND 1
Seen in one second: a big headline with a cobalt block in it, on a nearly empty grey screen (the hero drawing never opened).
Idea (one sentence): the cyclone sits in the headline where the word would be; the season's dates drive the check.
Live thing: cyclone-season check with countdown.
Layout words by section: hero=sky title / intro=centred statement / services=axis rows / steps=staircase / check=cobalt split / reach=pinned frame / about=drop cap / faq=indented list / contact=address as type / footer=cropped name
Scores: design 4 · usability 6 · creativity 7 · content 7 → overall 5.5
Caps applied: inspector FAILs (≤6.0); fewer than four real pictures (design ≤6.5)
Top three problems:
1. Hero drawing invisible (desktop-fold): the shutter waited on an observer that never fires for a fully clipped element. Fixed: open on load.
2. Pages scroll sideways at 1440 and 768 (staircase lines set nowrap; FAQ tiles bleeding past the margin). Fixed.
3. Nav links wrapping and 10 font sizes. Fixed: flex nav, sizes cut to five plus the footer name.

ROUND 2
Seen in one second: a cane-country landscape under a wet-season sky, "Mackay IT, ready for [cyclone] season".
Scores: design 6.5 · usability 7.5 · creativity 7 · content 7 → overall 6.95, capped at 6.0
Top three problems:
1. The supporting line collided with the mill and shed (desktop-fold): moved to the drawing's real horizon, computed from the slice ratio.
2. Cane read as a picket fence: regenerated as three rows of individual blades.
3. Map stages never switched and the closest zoom sat in the sea: observer fixed, coastline and street level redrawn, each stage centred.

ROUND 3
Seen in one second: same hero, with the supporting line now on the horizon and the mill between its halves.
Scores: design 6.5 · usability 8 · creativity 7 · content 7 → overall 7.1, capped at 6.0 (few-pictures FAIL)
Caps applied: inspector FAIL few-pictures (overall ≤6.0); fewer than four real pictures (design ≤6.5); the idea partly passes for another North Queensland MSP (creativity ≤7)
Remaining:
1. No real photographs or footage: every picture source was blocked by this environment's network policy.
2. Tablet hero: the second half of the supporting line crosses the mill stack at 768px.
3. The check's left column ends early, leaving its lower half empty on desktop.

## Deviations from the dealt sheet
- Type: Instrument Sans instead of General Sans (fontshare.com unreachable here). Self-hosted in fonts/.
- Pictures: all drawn in SVG; none found or dealt (all image hosts unreachable).
- Showcase zoom: 2× and 7.5× instead of 1.8× and 3.2×, so the third distance reaches street level.
- Footer on the surface tone rather than inverse, so it doesn't merge with the dark contact section.
- Contact keeps 72svh on desktop instead of 100svh (a full screen left a blank band).
