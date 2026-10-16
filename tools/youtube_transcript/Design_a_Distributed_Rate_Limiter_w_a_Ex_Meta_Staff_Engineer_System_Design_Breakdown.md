# Design a Distributed Rate Limiter w/ a Ex-Meta Staff Engineer: System Design Breakdown

Source: https://www.youtube.com/watch?v=MIJFyUPG4Z4

[00:00] All right, welcome back everybody. Today
[00:02] we are going to be breaking down a
[00:03] system design interview classic. We're
[00:05] going to be designing a rate limiter. Uh
[00:08] especially if you're new to system
[00:09] design, this is a fantastic place to
[00:11] start. It's a good problem to get
[00:12] familiar with. It's still incredibly
[00:14] popular at many of the top companies.
[00:15] It's asked a lot at Microsoft, for
[00:18] example, and many users recently have
[00:20] been reporting that it's being asked at
[00:21] OpenAI lately, too. Uh now, for those of
[00:24] you who are new to the channel, I'm
[00:25] Evan. I'm a former meta staff engineer
[00:27] and I'm the co-founder of Hello
[00:29] Interview. Hello Interview is a platform
[00:31] that helps people just like you prepare
[00:33] for upcoming software engineering
[00:35] interviews. And so if you haven't
[00:36] already, head over there, check it out.
[00:39] Now, if videos aren't your thing, we
[00:41] have detailed written writeups on this
[00:43] problem, designing a rate limiter, as
[00:45] well as 26 others. You can see them all
[00:48] here. We also have foundational core
[00:50] concepts, deep dives into technologies,
[00:53] patterns that we think are important to
[00:54] know for system design, as well as
[00:56] plenty of content on DSA, behavioral,
[00:58] salary negotiation, interview guides.
[01:00] You got it or you name it, we got it.
[01:03] Um, now you can also try this problem
[01:06] yourself using our guided practice. And
[01:09] so you can come here, fill things out
[01:11] step by step, record your answer, get
[01:14] feedback, and this is going to be
[01:15] evaluating your design in real time for
[01:18] each question along the way, letting you
[01:20] know what you did well, and of course
[01:22] the things that you can do in order to
[01:24] improve. So feel free to give that a go.
[01:26] The overwhelming majority of the content
[01:28] is free, guided practice. Everybody gets
[01:30] one for free from then on.
[01:32] Unfortunately, it's only for premium
[01:33] members. Hope you understand. All right,
[01:36] without further ado, let's get after it.
[01:41] Well, what even is a rate limiter?
[01:43] Chances are most of you are already
[01:44] familiar, but it's good for us to go
[01:46] over it so that we have a a shared
[01:48] understanding before we design the
[01:49] system. Rate limiters control how many
[01:51] requests a client can make in a specific
[01:53] time frame. And so, think about you have
[01:55] a social media app. Users are making
[01:57] requests in order to view news feeds,
[01:59] update posts, etc. And the rate limiter
[02:02] limits them to something like, for
[02:03] example, 100 requests per minute per
[02:06] user. And the whole point here is to
[02:08] protect our backend. It's to protect our
[02:10] services so that users can't come and
[02:12] abuse our system, spamming us with
[02:14] thousands of requests that ultimately
[02:16] might take down our system or make it
[02:18] unusable for other users. So that's what
[02:21] a rate limiter is. Now, before we jump
[02:23] into designing it, as we always do in
[02:25] these videos, we're going to outline the
[02:27] framework that we're going to follow
[02:28] both in this video and that I suggest
[02:30] that you follow in any of your real
[02:32] system design interviews. And so this is
[02:34] the hello interview delivery framework.
[02:35] We suggest you go step by step through
[02:37] these steps starting first with your
[02:39] requirements. This is where we're going
[02:41] to define both the functional
[02:42] requirements or the features of the
[02:44] system as well as the non-functional
[02:46] requirements or the qualities of the
[02:48] system. We're also going to outline some
[02:50] of the core entities. These are usually
[02:52] the nouns of your of your system. These
[02:54] are the uh the rows that you're storing
[02:56] or the um the tables, excuse me, in your
[02:59] database. The things that are exchanged,
[03:01] the resources in your APIs, that's our
[03:03] core entities. And then we'll do either
[03:05] API or system interface. In the case of
[03:08] a rate limiter, which is like a a
[03:09] back-end component, you know, the
[03:11] client's not necessarily interacting
[03:12] with it directly. We're going to focus
[03:15] on the system interface. Um, for some
[03:18] system design interviews, data flow
[03:19] makes sense. You could have it make
[03:21] sense here in designer rate limiter.
[03:22] think we'll probably skip it and we'll
[03:24] go right to the highle design where the
[03:26] goal of the highle design is to head
[03:27] over to the whiteboard, draw some boxes
[03:30] and arrows in order to satisfy those
[03:32] core functional requirements of the
[03:34] system. And so in other words, get a
[03:36] minimal design down early in your system
[03:39] design interview that's able to fulfill
[03:41] the basic features of the system. And
[03:43] then from there, we can move on to our
[03:45] deep dives where we're going to layer on
[03:47] complexity by satisfying our
[03:49] nonfunctional requirements such that our
[03:52] final design has everything it needs to
[03:53] be able to scale, be low latency, fault
[03:56] tolerance, all of those things that are
[03:58] really important. And so you'll watch me
[04:00] walk through this step by step. We'll do
[04:03] it together and we'll have some fun.
[04:08] for rate limiter specifically. Let's
[04:10] jump right in then with our functional
[04:12] requirements. Again, functional
[04:14] requirements. Functional requirements
[04:16] are the features of the system. Now, for
[04:19] userf facing applications, this is
[04:20] usually pretty straightforward. A user
[04:22] can write a post, a user can view a
[04:24] feed, whatever it may be. Uh, in the
[04:27] case of these backend components, it's
[04:28] sometimes a little bit more abstract,
[04:30] but I think it's still rather clear what
[04:32] needs to happen here. And so, I'm going
[04:34] to do this in order of when a request
[04:36] comes in. Well, the first thing is that
[04:38] the the the application the rate limiter
[04:40] here needs to be able to identify users
[04:44] by you know something. In our case,
[04:46] maybe this is their ID, their IP or even
[04:50] an API key, right? So, the most
[04:52] important thing is the rate limiter
[04:53] needs to know who is this because I need
[04:55] to determine whether or not I should
[04:56] limit them based on how many requests
[04:58] they've already made. So, that's step
[04:59] one. The second thing and the most
[05:02] important thing is that we need to be
[05:03] able to limit requests, right? We need
[05:06] to be able to limit requests and these
[05:07] should be based on configurable rules.
[05:10] And so a configurable rule here might be
[05:11] that any user can only make a 100
[05:13] requests per minute, maybe even to a
[05:16] specific endpoint, right? And so we got
[05:19] to identify a user and then we'll limit
[05:21] the requests that that user can make
[05:23] based on a set of configurable rules.
[05:25] And then the last thing is that we want
[05:27] to return proper error headers and
[05:30] status codes to the user. And so we
[05:32] don't want to be ambiguous here. We
[05:34] don't want to just return a failure of
[05:35] 500 to the user and them have no idea
[05:37] why. We want to tell them that they're
[05:39] being rate limited and maybe even give
[05:40] them some additional metadata so that
[05:42] they can deduce how they should uh you
[05:45] know move forward, what they should do
[05:47] next. So those are our functional
[05:49] requirements of our system at our core.
[05:51] That's what we're designing. Now, before
[05:53] you move on to the non-functional
[05:54] requirements in your interview, my
[05:56] suggestion to you is always check in
[05:57] with your interviewer at this point and
[05:59] ask them about the scale of the system.
[06:01] Especially in the case of of a rate
[06:03] limiter here, the scale is actually
[06:05] really interesting and there's a lot of
[06:06] questions that you'd want to ask. And
[06:08] so, I would ask my interviewer, what am
[06:10] I rate limiting? Is this a userfacing
[06:12] application like a Facebook or
[06:14] something? Is this some developer
[06:16] tooling? Is this rate limits um between
[06:19] intra microervices maybe within a
[06:22] company? What am I rate limiting? And
[06:23] now when I ask this question and as is
[06:25] most popular, you're typically going to
[06:26] be rate limiting some, you know, userf
[06:29] facing application like a social media
[06:30] app. And so we'll say that we have 100
[06:33] million daily active users and that
[06:36] means 1 million requests per second.
[06:39] Okay? So we have 1 million requests per
[06:42] second. Um, and we're going to be rate
[06:44] limiting at that particular scale. Now,
[06:47] one other thing I actually want to note
[06:48] here is that when I ask this question,
[06:49] this is kind of funny. Candidates would
[06:51] always say to me, "Am I designing a
[06:53] back-end rate limiter, uh, a serverside
[06:55] rate limiter, or a client side rate
[06:58] limiter?" And I'm going to be honest,
[06:59] this question was always a little bit
[07:01] confusing to me. It's like, of of course
[07:02] we're designing a serverside rate
[07:04] limiter. A client side rate limiter
[07:06] maybe doesn't provide nearly as much
[07:08] value in this case. It can obviously be
[07:09] spoofed. You can't trust the clients to
[07:11] limit themselves, right? And so I found
[07:15] out that candidates were always asking
[07:16] this because as I was doing some some
[07:18] research to write up our breakdown of
[07:20] this problem, I saw that most other
[07:22] writeups online start with that the
[07:24] server side or client side. Um, and so I
[07:27] don't know, like I said, I think this is
[07:29] a little silly. It's going to be server
[07:30] side. There are realistic use cases
[07:32] where client side provides some added
[07:34] value, but I've almost never seen it
[07:35] asked in an interview. Um, so bit of a
[07:37] tangent or or an aside from me, but yes,
[07:39] we're going to be doing a server side um
[07:42] rate limiter that is going to rate limit
[07:45] um for an application that has a 100
[07:47] million daily active users and 1 million
[07:49] requests per second. And so with that,
[07:51] we can come to our non-functional
[07:54] requirements.
[07:56] And so non-functional requirements trip
[07:58] up a lot of candidates. What is a
[08:00] non-functional requirement first of all?
[08:02] Well, if a functional requirement is the
[08:04] features of a system, right? what does
[08:05] the system need to be able to do? The
[08:07] non-functional is how does it need to be
[08:09] able to do it? And so this is where
[08:11] there's all those illity statements,
[08:13] right? This is where you're going to
[08:14] talk about scalability, low latency,
[08:16] durability, um even security, fault
[08:19] tolerance. Now, if you head over to
[08:21] hello.com under the delivery framework
[08:24] section, we list off all the things that
[08:25] you should consider in the
[08:26] non-functional requirement. But most
[08:29] importantly, you're not going to just
[08:30] write all of those things. Everything
[08:32] you write in the non-functional
[08:34] requirements, you're expected to address
[08:35] in your design. This is really crucial.
[08:38] And so you're going to want to call out
[08:39] the specific column illities, right?
[08:42] Ilies, um, that are directly relevant to
[08:45] this design. Okay? And so pick out the
[08:47] ones that you think are most specific
[08:49] and most interesting and we'll go
[08:50] forward with those. And so the first
[08:52] thing that you you want to consider in
[08:53] your non-functional requirements is
[08:55] always cap theorem. And so of course in
[08:57] CAP theorem, we have consistency,
[08:59] availability, and partition tolerance.
[09:01] Partition tolerance is a must. So your
[09:03] decision is always should my system be
[09:05] strongly consistent meaning should every
[09:08] single read be reading the latest write
[09:10] or should we opt for high availability
[09:13] and thus eventual consistency is fine.
[09:16] Now in our case we're going to go for
[09:19] availability over consistency. You can
[09:22] think of this like if somebody was going
[09:23] to push a new rule to our system, would
[09:26] we rather that the rate limiter still
[09:28] works even if it's reading outdated
[09:30] rules for a bit while they're
[09:31] propagating or should we have the rate
[09:33] limiter basically go offline because we
[09:35] need to wait until all rules have
[09:36] propagated. That's one example of
[09:38] availability versus consistency.
[09:39] Clearly, we want to make sure that our
[09:41] rate limiter is still always just up and
[09:43] available and working because it's
[09:44] protecting our system. Now, the second
[09:47] thing that is uniquely interesting to a
[09:48] rate limiter is low latency. And so in
[09:52] any system design interview, a bad
[09:54] candidate or I shouldn't say bad but
[09:55] maybe a a less good candidate would come
[09:57] in here and they would write this on the
[09:58] board low latency. And I as the
[10:01] interviewer would say like okay yes
[10:02] systems it's good for a system to be low
[10:04] uh have low latency but what do you mean
[10:07] here? And now what a good candidate
[10:09] would do is they would be specific and
[10:11] they would say we have low latency rate
[10:13] limit checks and even better we're going
[10:17] to aim for under 10 milliseconds.
[10:19] And so what they've done here is that
[10:21] they've both quantified and they've also
[10:24] qualified. So they said, I want low
[10:26] latency in the case of a user making a
[10:29] request. We don't want to add additional
[10:31] latency to their request. And then we
[10:33] want to make sure that we add less than
[10:34] 10 milliseconds. And this is what
[10:35] they're going to try to design for. Now,
[10:37] of course, this is really important in a
[10:39] rate limiter because your rate limiter
[10:40] is adding additional time to any request
[10:42] from a user. that user requested
[10:44] something like uh a post and we're going
[10:47] to take time to first check if they're
[10:49] allowed to view that post based on their
[10:51] rate limits, but we don't want to take a
[10:52] long time doing it. The user wants to
[10:54] see that post quickly, right? So low
[10:55] latency is important there.
[10:58] And then we we sort of already implied
[11:00] that this was important when we talked
[11:01] about scale question above, but this
[11:04] system needs to be scalable. So
[11:06] scalability, right? So it needs to be
[11:08] scalable scalable and we want to scale
[11:11] again to quantify it to that 1 million
[11:15] requests per second. And so the goal of
[11:19] our functional and our non-functional
[11:21] requirements is to agree with our
[11:23] interviewer exactly on what we're
[11:24] building. We're basically setting up
[11:26] this contract with them saying that for
[11:28] the rest of the interview, these are the
[11:29] things that I'm going to fulfill. And
[11:31] now I as the candidate can hold myself
[11:33] accountable because if I get to the end
[11:34] of the interview and I did all of these
[11:36] things well, I kind of did all six of
[11:38] these things here well, then I should
[11:40] feel confident leaving the interview
[11:41] like I passed and I nailed it. And
[11:42] that's the general goal here. Um, and so
[11:45] at this point, check in with your
[11:46] interviewer. Ask them, is there anything
[11:48] I'm missing? Is there anything you would
[11:50] change? Otherwise, I'd love to continue
[11:52] and move on to the next sections.
[11:58] The next sections for us is the core
[12:00] entities in the interface. Now, I'm
[12:02] going to admit for these backend
[12:03] components, this is slightly less
[12:04] important again than a userfacing
[12:06] application, but they do form a basis
[12:09] and they're they're not steps I would
[12:10] skip, but you can probably do them
[12:12] frankly in in under a minute. And so,
[12:14] let's do that. Let's kind of breeze
[12:15] through them. What are the core entities
[12:17] of a system like this? Well, the core
[12:19] entities that you have is a request.
[12:21] This is the request that's incoming. Uh
[12:23] it's how you are going to determine who
[12:25] is making the request, right? And so
[12:27] like the who I'm going to call them a
[12:29] client, but this is like your IP
[12:31] address. This is your user ID, the
[12:34] things that we talked about earlier,
[12:35] maybe your API key, right? So you have a
[12:37] request come in, you have a client, and
[12:38] then you have rules. Of course, these
[12:40] rules are the things like, you know, 100
[12:43] requests per user per second, right? So
[12:48] very simple. Those are the core entities
[12:50] of our system. They're good for getting
[12:52] us to wrap our head around what's going
[12:53] on here. and they lead us nicely to what
[12:55] would be either our API or a system
[12:58] interface. Now I'm going to go with
[13:00] system interface instead of API because
[13:03] we want to choose API when we're doing a
[13:05] userfacing application where users are
[13:07] calling an API. Users are not calling an
[13:09] API in this case. users are are calling
[13:11] an API of for example our social media
[13:14] app right get posts but it's us who are
[13:17] checking the rate limiter and we're
[13:19] doing this via probably an RPC call or
[13:21] some internal call um which we can
[13:24] define as our system interface and so
[13:26] you can do this however you want I like
[13:27] to do it kind of as a function call and
[13:30] really it's just this one function that
[13:32] we're implemented is this request
[13:34] allowed right for this client ID in this
[13:37] rule and we're going to return basically
[13:40] Did it pass? You know, is that allowed?
[13:43] True or false? Um, we should also return
[13:45] though, if we look back to our
[13:46] functional requirements, we wanted to
[13:48] return some interesting stuff here. So,
[13:50] the user knows what to do. And some of
[13:52] those interesting things might be, you
[13:54] know, how many remaining requests the
[13:57] user may have if they do pass. Uh, as
[13:59] well as like maybe what time it resets.
[14:02] You know, this would depend on what our
[14:03] algorithm is, which we'll get into in
[14:04] more detail later. But this is the thing
[14:07] that we're implementing, some function
[14:09] that allows us to ask if a request
[14:11] passes or not. And so if we zoom out
[14:15] now, we should have a pretty good
[14:16] understanding. This was our setup. We
[14:18] have a good understanding of what we
[14:19] want to build. We've done our
[14:20] requirements, our entities, and our
[14:22] interface. And it's time for us to head
[14:24] over to the whiteboard, do the really
[14:25] fun stuff, start drawing boxes and
[14:27] arrows, nail down our highle design, and
[14:29] then our deep dives.
[14:33] As we get into our high level design, uh
[14:36] the approach that we take here is
[14:37] actually really simple and methodical.
[14:39] You don't need to overthink this. You're
[14:40] just going to go one by one through your
[14:42] functional requirements in order to make
[14:44] sure that we can satisfy each of them.
[14:46] And so our first requirement is that the
[14:48] system should be able to identify
[14:49] clients by their user ID or IP address
[14:53] or API key and so on. But importantly,
[14:55] maybe before we can limit anyone,
[14:57] there's two key questions that we need
[14:59] to be able to to answer. And so I'll
[15:01] write them over here so that we have
[15:02] them in mind. The first is where should
[15:05] our rate limiter live in our
[15:08] architecture? Basically, where do we
[15:10] place it? Right? And this is going to
[15:12] determine what information we can access
[15:14] and how it integrates with the rest of
[15:16] the system. And then the second question
[15:18] that we're going to need to be able to
[15:20] answer is how should we identify
[15:22] clients? And so based on those user ID,
[15:25] IP address, uh API key, anything else,
[15:29] what's the right way to identify a user?
[15:31] And this assures that we of course apply
[15:32] the rate the right rate limits to to any
[15:35] given user. And so these two questions
[15:38] here, they're closely linked. Your
[15:39] placement choice is going to affect what
[15:41] client information you can easily
[15:43] access. And your identification strategy
[15:46] influences where the rate limiter makes
[15:48] the most sense to deploy. And so let's
[15:51] start with with the first one here.
[15:53] Where should we place the rate limiter?
[15:54] That's the first thing that we're going
[15:55] to answer. And we have three main
[15:57] options. Now the first option is pretty
[16:01] maybe obvious and we can start with the
[16:03] simplest thing. Let me draw out why is
[16:05] that so thick? Uh let me draw out what
[16:07] our basic system could look like. Right?
[16:10] So we're going to have some client.
[16:12] We're going to have a microser
[16:13] architecture because we have some large
[16:16] system here like our um uh uh what did
[16:21] we call it? Social media app. Excuse me.
[16:23] Hard to type and think.
[16:27] And so here's just our really basic
[16:28] setup. Okay, clients make requests to
[16:31] our social media app. It goes to our
[16:33] gateway. Our gateway then forwards that
[16:35] on and routes it to the appropriate
[16:37] micros service. That micros service does
[16:39] its thing and returns back to the
[16:41] client. Okay, so there's the basics of
[16:42] our social media app. And now we need to
[16:44] stick a rate limiter somewhere. We
[16:46] talked about putting a rate limiter on
[16:47] the client doesn't make as much sense.
[16:48] We alluded to that in the beginning. So
[16:50] we need some uh rate limiter back here
[16:52] in the back end or in server code. So
[16:55] where can we place it? The first option,
[16:58] I'll make it blue here, is that we can
[17:01] put our rate limiters directly inside
[17:04] each of our respective
[17:07] microservices. Right now in this setup,
[17:10] it's just part of your application code.
[17:11] And so when a request comes in, the
[17:13] server is going to check its local
[17:14] memory for the current counts for any
[17:16] given user. It'll update them and then
[17:18] decide whether to allow or reject the
[17:20] request. Now the good thing is this
[17:22] approach is extremely fast. Everything
[17:24] is happening in memory. There's no
[17:25] network calls. There's no external
[17:27] dependencies. But the downside I think
[17:29] is is really obvious. There's no global
[17:31] picture. And so you can imagine that a
[17:33] user makes two requests where one hits
[17:35] microser one and one hits micros service
[17:37] 2. And in each case they both think that
[17:40] only one request has come in. However,
[17:42] of course, globally the user has made
[17:44] two requests. And so the lack of
[17:46] coordination makes this a really poor
[17:48] option. And so what's the the second
[17:51] thing we could do? Well, naturally, we
[17:53] could pull this out and maybe make this
[17:55] rate limiter its own service here,
[17:59] right? Make it global. And so now, every
[18:01] time a request comes into one of these
[18:03] microservices, the first thing that
[18:04] they're going to do is check with the
[18:07] rate limiter and say, "Hey, am I allowed
[18:09] to process this request?" Basically, is
[18:12] this under our limits? And if yes,
[18:14] they'll end up processing the request uh
[18:16] and sending the results back to the
[18:18] gateway or back to the client through
[18:19] the gateway. And so this is great and
[18:21] that it solves that global coordination
[18:23] problem that we were worried about.
[18:25] Wonderful. Um but it also is going to
[18:27] introduce some excess latency. And so
[18:29] now every single request that comes in
[18:31] is going to go from the gateway to a
[18:32] microser. The microser is then going to
[18:34] make a network call to a separate
[18:36] service, a separate server somewhere
[18:37] which is your rate limiter which is
[18:39] going to respond and then it's going to
[18:40] do its thing and respond back to the
[18:42] user. And so admittedly this is fairly
[18:45] minimal. Um, but just keeping in mind we
[18:49] had those tight latency requirements and
[18:51] so we want to make sure this is as quick
[18:52] as possible. Um, and this added network
[18:55] overhead probably isn't worth it. And so
[18:57] how can we keep that global picture but
[19:00] maybe reduce the latency of that network
[19:02] overhead. And now the the answer and
[19:05] what is used in most production systems
[19:08] is to actually just move the gateway
[19:09] over here to the edge. And so we can
[19:12] place it directly in either our API
[19:14] gateway or our load balancer, whatever
[19:16] component sits at the front of our
[19:18] system at the edge of our system. And
[19:20] now in this setup, every single incoming
[19:22] request is going to hit our rate limiter
[19:24] first. And so right before we determine
[19:27] where to route this request to, we'll
[19:28] just say, hey, can we even service this
[19:30] request based on our our given limits?
[19:33] Right? And so for those of you maybe who
[19:36] like analogies, you can think of this
[19:38] placement of our rate limiter like like
[19:40] a bouncer at the club. I think is the
[19:42] kind of silly but canonical example
[19:43] here, right? And so troublemakers are
[19:46] going to get turned away at the door,
[19:48] not after they're already made it inside
[19:50] and started to cause problems like was
[19:52] the case in the previous approach.
[19:54] Right? Now, this this still has some
[19:57] some limitations. The first is around
[19:59] scale, but that's fine. We'll talk to
[20:00] that as we get to our non-functional
[20:02] requirements. But more importantly, this
[20:04] limits the amount of context that we
[20:06] have. And so when we had the rate
[20:08] limiter in our application code, we in
[20:10] theory have context to everything about
[20:12] our system. And so if you want to make
[20:14] complex rate limiting rules like you
[20:16] know rate limit somebody differently
[20:17] based on whether they're a premium user
[20:19] or something that was easy to do. But
[20:21] now as we sit at the edge we only have
[20:24] information that came in via the HTTP
[20:26] request itself. So the headers, the URL,
[20:29] the IP address and and any basic
[20:31] authentication tokens that are present
[20:32] in the actual request. we can't see that
[20:35] deeper business logic that might exist
[20:37] inside of our application code with
[20:39] access to to some persistent storage
[20:41] like a database. And so this is fine to
[20:44] give that example again. Maybe we want
[20:46] to to do the premium user thing. Premium
[20:48] users get 10x higher rate limits. Um
[20:50] it's still doable. We just need to make
[20:52] sure that the fact that a user is a
[20:54] premium user is encoded in the request.
[20:56] This is typically via the JWT token
[20:59] which is going to be in the headers. And
[21:00] so anything the clients send over should
[21:02] say in this case via the JWT that
[21:04] they're a premium user. So we have that
[21:06] context. We do our rate limiting. And
[21:08] then our microservices can focus only on
[21:11] servicing requests. They don't need to
[21:13] know about anything about how we we rate
[21:16] limit or whether we rate limit. Now we
[21:17] want to answer that second question that
[21:19] we outlined and that's how should we
[21:20] identify clients. Well to be honest
[21:22] we've kind of been talking about this
[21:23] the whole time. We even put it directly
[21:25] in our functional requirement with user
[21:27] ID, IP, API key, etc. But this is
[21:30] something that you're going to want to
[21:30] bring up and talk to your interviewer
[21:32] about. It's basically what makes a
[21:34] client unique. And those are the three
[21:36] main options. The user ID, the IP
[21:38] address, or the API key. Uh, but this is
[21:41] a perfect time to ask your interviewer
[21:43] some questions. And I would ask them,
[21:45] are all of our users authenticated? Is
[21:47] this a developer API that's going to
[21:49] require an API key? Etc. These are the
[21:52] sorts of things that you might want to
[21:53] ask. But in practice, and this would
[21:55] maybe be the most impressive answer to
[21:56] give your interviewer, is that we're
[21:58] probably going to want a combination.
[22:00] Maybe authenticated users get higher
[22:02] rate limits than anonymous IP addresses.
[22:04] Or as we talked about earlier, premium
[22:06] users may get even more. This is a
[22:08] reflection of your understanding of like
[22:10] real world systems. And you're not going
[22:12] to enforce just a global limit, but
[22:14] probably have layers of multiple rules.
[22:16] And so you might have Alice can make a
[22:19] thousand requests per second. any given
[22:20] IP address can make a 100 requests per
[22:22] second. Uh an API can handle 50,000
[22:26] requests per second. You know, whatever
[22:28] it may be. So, we're going to be able to
[22:30] identify all of these things, apply them
[22:32] to different rules, and they're going to
[22:34] be identified as we've talked about just
[22:36] via the request, usually from the
[22:37] request headers. Now, we can move on to
[22:40] our second functional requirement where
[22:42] it's the system should limit requests
[22:44] based on configurable rules. And so this
[22:47] is where we get to the heart of rate
[22:48] limiting and that is the algorithm that
[22:50] decides whether we should allow or
[22:52] reject any given request. Now
[22:54] importantly in system design interviews
[22:57] this this being the algorithm isn't
[22:59] actually usually the main focus of the
[23:01] interview unlike is the case in
[23:02] low-level design interviews. Now you're
[23:04] still going to want to be able to
[23:05] acknowledge that you know the different
[23:07] options that you can weigh the different
[23:08] trade-offs and explain and justify your
[23:10] choice but you likely won't need to
[23:12] implement it not even in pseudo code. So
[23:15] with that said, there are many different
[23:17] rate limiting algorithms, but I think
[23:18] there's four that are worth you knowing.
[23:20] And so let's start with the simplest and
[23:22] we'll work our way up. The simplest is
[23:24] what's known as the fixed window window
[23:27] counter. And it's incredibly
[23:29] straightforward. Users get n requests
[23:32] per window. So for example, 100 requests
[23:34] a minute. And for each user, we're going
[23:37] to maintain a counter that resets at the
[23:39] start of each window. If the counter
[23:40] exceeds the limit during that window, we
[23:43] reject the request. And so, let me I
[23:45] probably should have pasted this in a
[23:47] moment ago, but here is the diagram that
[23:49] we have in the article to work with
[23:51] here. And so, these are each window
[23:53] interval. Requests come in. In this
[23:56] simple diagram, it looks like we have
[23:57] three requests per window until we start
[23:59] to reject. You get to your fourth
[24:01] request, it passes that threshold, and
[24:04] we end up ultimately rejecting it. Um,
[24:08] now the upside of this is that it's
[24:10] really, really trivial to implement. You
[24:11] just need a hash table that can map your
[24:13] client IDs to counter and window start
[24:16] pairs. And so that hash table might Oh,
[24:20] let's see if I can copy that better.
[24:22] That hash table might look something
[24:24] like this, right? Where you just have
[24:27] Alice at 12, she had 100 requests. At
[24:31] 12:01, she had five requests. Bob,
[24:33] Charlie, Dave, Eve, and Frank,
[24:35] respectively. So really really really
[24:37] easy to implement. But the downside is
[24:40] what we end up calling the boundary
[24:43] effect. And so a user can make a 100
[24:45] requests at 1201 and 59 seconds. And
[24:50] then at 1202 they can make 100 more
[24:53] requests because they went on either
[24:55] side of the boundary here. And thus they
[24:57] ended up in effect making 200 requests
[25:00] in just 2 seconds, right? Which which
[25:02] isn't great. The other thing is that
[25:03] there's the option for starvation. And
[25:05] so if you made your 100 requests at
[25:07] 12:01 and 1 seconds, now you have to
[25:09] wait 59 seconds until you can make any
[25:12] requests at all, which depending on your
[25:14] needs might also be a problem. Now the
[25:16] second approach is called the sliding
[25:18] window log. Sliding Why am I blue?
[25:22] Sliding window log. And it basically
[25:26] just smooths out the issues that we had
[25:28] with the fixed winner counter. And so
[25:30] let me get this new drawing in here for
[25:31] you. Right? And as the name implies, we
[25:35] have the sliding window. And so as
[25:37] requests come in, we keep track of this
[25:39] rolling window over the last minute. And
[25:41] we just say something like we can only
[25:43] have 100 requests in the last rolling
[25:46] minute. Right now, this eliminates the
[25:48] boundary effects and the burst problem
[25:50] from the fixed window counter that we
[25:52] had over here because it tracks the
[25:54] exact time of each request, which is
[25:55] going to give you that perfect accuracy.
[25:57] However, the downside here is that this
[25:59] is typically implemented implemented
[26:01] with a heap or a deck. Um, and this is
[26:04] going to require a ton more memory. And
[26:06] so, if you have a ton of users, this is
[26:08] going to be tons more memory. Um, it's
[26:11] more memory per users and it's going to
[26:13] need a bunch more instances and it's
[26:14] going to be more expensive. So, that's
[26:16] the potential downside here. So, the
[26:18] third algorithm addresses the memory
[26:19] issues that we have with the sliding
[26:21] window log um by using what we call a
[26:23] sliding window counter. And it's
[26:26] basically the the sliding window log but
[26:28] with some mild optimization so that we
[26:30] don't have to keep every single time
[26:32] stamp that comes in in something like a
[26:33] heap. Right? We can be clever and
[26:35] instead just keep two counters. One for
[26:38] the previous fixed window and one for
[26:40] the current window we're in right now.
[26:42] And now the key is that we estimate what
[26:44] a true sliding window would look like uh
[26:46] by weighing these two fixed windows
[26:49] based on how far we are into the current
[26:51] window. And so let me just show you an
[26:53] example. I have an example written here
[26:55] that I can paste in. And so imagine that
[26:58] the previous window from 1 minute to 1
[27:00] minute 1 second had eight requests. And
[27:03] now we're 42 seconds or 70% into our
[27:06] second window. And so far we have six
[27:09] requests. Well, should we accept the
[27:12] next request? Right. Well, here's the
[27:14] math. Given that we're 70% through the
[27:17] minute, we can take our current requests
[27:20] as well as 30% of the last window,
[27:24] right? 30% of the last window. This is
[27:26] us estimating how many more should we
[27:29] get in the remaining 30% of the window,
[27:32] right? This is going to estimate that
[27:33] we're at 8.4. Now, if our limit was 10,
[27:36] we could say 8.4 is less than 10 and
[27:38] thus we should pass. And the great thing
[27:41] here is that this gives us much better
[27:43] accuracy than those fixed windows, but
[27:46] we only need to use two integers per
[27:47] user. We don't need to keep a whole heap
[27:49] per user, right? So downside, it's an
[27:52] approximation. Uh it's not perfect. It's
[27:54] not going to be perfectly evenly or
[27:56] excuse me, it's an approximation and it
[27:58] assumes that requests are pretty
[28:00] perfectly evenly spread across each of
[28:02] these windows, which aren't necessarily
[28:04] the case. But if you can handle this
[28:05] approximation, it's a pretty decent
[28:08] option.
[28:09] Now, the last option and and the one
[28:11] that is is arguably most popular and the
[28:13] one that we're probably going to go with
[28:15] is what's called the token bucket. So,
[28:17] let me paste in my cute little drawing
[28:19] here. Hopefully, you guys like this one,
[28:21] right? But you can think of it as each
[28:23] client has their own bucket that holds a
[28:25] certain number of tokens. And these
[28:27] number of tokens in the bucket, they're
[28:29] the burst capacity. Okay? And now at the
[28:32] same time, token tokens are being added
[28:34] to the bucket at a steady rate. And
[28:37] these are called the refill rate. And
[28:39] every time a request comes in, we
[28:42] consume one token. If there are no
[28:44] tokens available, then the request is
[28:47] rejected. Right? So that sounds a little
[28:49] confusing, but it accomplishes two
[28:50] things really nicely. The size of your
[28:52] bucket is how you handle bursts. Those
[28:54] bursts that we talked about earlier. And
[28:56] so if your bucket starts with 100, then
[28:58] I can handle a burst of 100 at any given
[29:01] moment, right? And then my refill rate,
[29:03] this is like the steady number of
[29:05] requests per minute or per time that I
[29:08] can handle. So if your refill rate was,
[29:10] you know, uh 60 uh 60 a minute, then
[29:14] we're going to add one new token every
[29:16] minute. And that means that our steady
[29:18] rate is going to be run one request a
[29:21] minute, right? And each time a request
[29:22] comes in, we pull it out. And so an
[29:25] example, a bucket holds, like I just
[29:27] said, 100 tokens. This is going to allow
[29:28] bursts of up to 100. If the refill rate
[29:31] was 10 tokens per minute, this is a
[29:34] steady rate of 10 requests a minute. And
[29:36] then clients can make a 100 requests
[29:37] immediately, but then they'll need to
[29:39] wait for the bucket to refill and
[29:41] they'll be at that slower rate. And so
[29:43] this is really great because it handles
[29:44] that sustained load via our refill rate
[29:47] and the temporary bursts by our bucket
[29:49] capacity. It's also shockingly simple to
[29:52] implement. You just need to track the
[29:54] tokens and the last refill time for
[29:57] every given client. So again, just two
[29:59] numbers, but the challenge is choosing
[30:01] obviously your right bucket size and
[30:03] your refill rate and how you handle cold
[30:04] starts and things like this. Um, but
[30:06] it's a pretty elegant algorithm and it's
[30:08] the one that we're going to to choose
[30:10] for our design here. So we understand
[30:12] how the token bucket algorithm works
[30:15] conceptually. But where and how do we
[30:17] actually store each user's bucket,
[30:20] right? How would we actually implement
[30:21] this? Each bucket needs to track two
[30:24] pieces of data. the current token count
[30:26] and the last refill time stamp. And the
[30:29] state needs to be shared across all the
[30:31] different instances of the API gateway.
[30:34] And so importantly, in a real production
[30:36] system, you're going to have multiple of
[30:38] these gateways. And so they need to
[30:40] share some global state. If they don't,
[30:43] then we run into the same problem that
[30:44] we talked about earlier when we sh
[30:46] stored specific uh rate limiters inside
[30:49] of each microser respectively. And so
[30:52] what we can do is we can pull the rate
[30:54] limiter state out into an in-memory
[30:58] cache something like Reddus. And so
[31:01] these token counts, these token counts
[31:03] and the last refill rate, all of that
[31:04] state can be shared here in Reddus such
[31:07] that even though we have multiple
[31:08] gateways, they'll all still going to
[31:11] read that same shared state. And so what
[31:15] actually is going to happen here? Well,
[31:17] maybe let's let's write this out for
[31:19] extreme clarity. First a request is
[31:22] going to come in of course. The second
[31:26] thing is that the gateway is going to
[31:28] fetch the token. And last
[31:32] and typing while you guys all watch is
[31:34] always difficult from Reddus.
[31:38] Okay. And so in Reddus we can use what's
[31:41] called an hm getit. And so what an hm
[31:43] getit is it allows you to get the values
[31:46] of multiple keys. And so we can say for
[31:49] Alice's bucket, we want the tokens and
[31:52] the last refill, right? So see that
[31:55] command there? That's pretty great.
[31:56] We're just saying in one command, give
[31:58] me her current tokens and the last time
[32:00] that it was refilled. Cool. And then
[32:03] what we can do then is calculate based
[32:06] on when her last refill time was, how
[32:09] many tokens we need to add to her
[32:11] bucket. And so this is really simple.
[32:12] So, if Alice's bucket was last updated
[32:14] 30 seconds ago and her refill rate is
[32:17] one token every second, then the gateway
[32:19] is going to need to add 30 tokens to her
[32:22] current count, right? So maybe her
[32:24] current count was 20. The last refill
[32:26] rate was 30 seconds ago. We refill at
[32:28] one every second. So now the count is
[32:31] 50, right? So the next step here is
[32:34] update counts based on rate and last
[32:39] last refill.
[32:40] [Music]
[32:42] Great. Right. And then of course we're
[32:45] going to respond pass or fail based on
[32:50] if token after the refill or excuse me
[32:53] if kind of tokens
[32:56] after that refill is greater than zero.
[32:59] Are there any tokens in the bucket given
[33:02] what was in the bucket and how much
[33:03] should have been refilled since the last
[33:05] time that we checked this. Are there
[33:07] greater than zero tokens? If yes then we
[33:10] can pass. Right. And then the fifth
[33:12] thing is to update the bucket status.
[33:14] And so this is where we will write back
[33:16] and update the token count to whatever
[33:18] that new token count is. Update whatever
[33:20] the the last or update the last refill
[33:23] time to whatever the current time stamp
[33:24] is. Right? So make sure that everything
[33:26] gets updated. That's the general flow.
[33:30] But importantly, hopefully this makes
[33:33] sense so far. There's a race condition,
[33:35] right? So I want you to imagine I want
[33:37] you to imagine the following. Let me try
[33:39] to illustrate this. I have gateway A and
[33:42] I have gateway B. And Alice sends in two
[33:46] requests. One request hits A, one
[33:49] request hits B. They both go and read
[33:53] Reddus for our token counts. Right? So
[33:56] they both go and say, "What is my
[33:58] current token and my current last refill
[34:00] rate?" Well, in both cases, they're
[34:03] going to read the same value. That value
[34:05] might be one, right? It comes back as
[34:08] one. They both check. Maybe the last
[34:10] time we checked was a second ago. There
[34:12] have been no more tokens added. So they
[34:14] both read. They both say, "Okay, it's
[34:16] one that's greater than zero. We're
[34:18] going to accept." They both accept and
[34:19] they both go right to Reddus. Maybe this
[34:21] one writes a nancond before than this
[34:23] one. So this one overwrites the
[34:25] previous. Right? The important bit here
[34:27] is that the race condition is that we
[34:29] have this read after write problem. You
[34:32] can have the read from a from gateway a
[34:34] then the read from gateway b then the
[34:37] right from a then the write from b when
[34:39] those two things the read and the right
[34:40] for each have to happen atomically right
[34:44] and so the key is that these things the
[34:47] one read from reddus and the two write
[34:50] back to reddus has to be atomic in a
[34:52] postgress database or anything this is
[34:53] done of course like via transactions
[34:55] with locking as well in the case of
[34:58] reddus it supports atomic transactions
[35:00] and it's single threaded which actually
[35:02] makes this a little bit easier and it's
[35:03] something called Luis scripting. Louis
[35:06] scripting. And so I'm not going to go
[35:07] into too much detail here, but the
[35:08] general essence is that you can have all
[35:10] of these uh Reddus commands, this hm
[35:13] getit, the h set in order to update the
[35:15] token counts all via a single reddus uh
[35:18] reddice or excuse me, a single reddis
[35:20] luis script, right? And then it'll go
[35:22] over the wire. It'll do the read and
[35:24] write all in one instance and then
[35:27] return to you whether or not you should
[35:28] pass or not. And that all happens
[35:30] atomically and you don't have the race
[35:32] condition. It's basically like one one
[35:34] does everything and the other one waits
[35:35] until the other one is completely
[35:36] finished. Okay, hopefully that makes
[35:39] sense. Um, okay, fantastic. So, what
[35:43] have we done here? Coming back, we have
[35:45] now covered our first and our second
[35:47] functional requirement. All that's left
[35:49] is that we need to return proper error
[35:51] headers and status codes. And this is
[35:54] this is pretty straightforward. This is
[35:56] the easiest one here. Um,
[35:59] I guess there is one decision that we
[36:00] want to make. Uh, and that one decision
[36:02] is that if a request, if we've exceeded
[36:07] a rate limit, what do we do? Do we
[36:09] reject immediately or do we cue it and
[36:12] wait and try to handle it later? This
[36:14] might seem obvious to many of you
[36:15] listening, and I've almost been alluding
[36:16] to this throughout. We're going to take
[36:18] the approach of what's called fail fast.
[36:20] And so, if we exceed the limit, we're
[36:21] immediately going to send a failure back
[36:23] to the user. We're not going to cue it.
[36:25] In a system like this, queueing doesn't
[36:26] make any sense. If a user is asking for
[36:29] posts to view their posts, we cue it.
[36:32] They're waiting and waiting and waiting.
[36:34] They think something is broken anyway.
[36:36] They hit the button again to try to view
[36:38] their post again. Now we just have a
[36:40] bunch of requests uh sitting in our
[36:42] queue and a backlog is growing. It
[36:44] becomes an even larger issue. And so
[36:47] there are niche cases where queuing
[36:48] makes sense like for batch processing
[36:50] systems that can afford to wait. This is
[36:52] usually like intra service
[36:54] communication. But for the interactive
[36:56] fast API like we have here, this fast
[36:58] failure fail fast is the most common and
[37:00] the right choice. Um, but how do we make
[37:03] sure then that our response is actually
[37:05] helpful? Well, the first thing that's
[37:07] worth noting that you're definitely
[37:08] going to want to know for an interview
[37:09] is that the HTTP status code that you're
[37:13] going to send on failure is a 429.
[37:16] 429 means too many requests and it is
[37:19] the standard HTTP status code that is
[37:22] used for exactly this. when you want to
[37:25] rate limit somebody because they've had
[37:26] so many requests, you send back a 429.
[37:29] Um, but there's some additional headers
[37:32] that are best practice that you want to
[37:34] send back to the client as well. Forgive
[37:36] me, I'm going to copy and paste it so
[37:37] you guys don't have to watch me fumble
[37:40] through typing anymore. Let me put them
[37:43] here. Right. So, you want to send back
[37:45] probably three additional things. The X
[37:47] rate limit limit. This is the rate limit
[37:50] ceiling for the requests. Right? So if
[37:52] you can have 100 per minute, that's what
[37:54] you're going to put in here. The x rate
[37:56] limit remaining, this is the number of
[37:58] requests left in the current window. Of
[38:01] course, the notion of a current window
[38:02] will depend on your algorithm. So this
[38:04] can get a little bit funky, but you want
[38:05] to give them some notion of where they
[38:07] are. And then the rate limit reset, when
[38:09] is this going to reset? Um, there's
[38:12] other ones like retry after is a common
[38:14] one that's added here too. Retry after.
[38:18] This will say, you know, try again in 60
[38:21] seconds.
[38:22] Now most importantly in your interview
[38:24] you should know 429. I think
[38:25] interviewers expect you to know the the
[38:27] response code is 429. But when it comes
[38:28] to like memorizing rate limit limit rate
[38:31] limit remaining rate limit reset retry
[38:32] after. Don't stress it. You do not need
[38:35] to memorize these in an interview. I
[38:37] would say something like the following.
[38:38] I would say I'm going to make sure that
[38:39] I return a 429 status code with the
[38:41] appropriate headers. Like some headers
[38:43] that can let the the user know when they
[38:45] can try again or how many are are
[38:47] remaining. Pretty clear.
[38:51] So we have our high level design in
[38:53] place. We're feeling pretty good about
[38:54] it. We chose our algorithm. The basics
[38:56] are all working here. But now we need to
[38:58] go back to our delivery framework. And
[39:00] next up is our deep dives. And so this
[39:02] is where we uh go one by one through our
[39:05] non-functional requirements in order to
[39:07] expand upon our design to make sure that
[39:10] each of those non-functional
[39:11] requirements are satisfied. And then we
[39:12] can really feel good about what we put
[39:14] here. So, I'm going to move some of this
[39:16] around just so that we have a bit more
[39:17] space. You guys will have this uh
[39:20] whiteboard linked below in the
[39:22] description for anybody that wants to
[39:23] reference it.
[39:25] Now, I'm going to go a little bit out of
[39:27] order when we talk about our
[39:28] non-functional requirements. I'm
[39:29] actually going to work with scalability
[39:32] first. We want 1 million requests per
[39:35] second. And if you come back to our
[39:37] current design, it should be relatively
[39:39] clear why this won't scale to a million
[39:41] requests per second. And the reason is
[39:43] that we have just this single Reddus
[39:45] instance. And so Reddus can handle, you
[39:48] know, somewhere on the order of
[39:50] depending on the hardware, maybe a
[39:52] 100,000
[39:53] requests per second or operations per
[39:56] second. And that's a tenth of what we
[39:58] need to be able to support. But of
[40:00] course, if you remember what we actually
[40:02] need to do, we need to do an HM get and
[40:04] we need to do an HM set. We need to do
[40:05] both of those things for every call. So
[40:07] that's two operations. Uh so maybe we
[40:10] can even say that with what we have we
[40:13] can support 50k requests per second. And
[40:18] what we need to do then is we need to
[40:20] shard. And sharding of course is the
[40:22] strategy for which we can introduce
[40:25] um more instances and shard the data
[40:28] across those instances. Okay. So you can
[40:30] take a large collection of data and then
[40:33] shard the keys of that data across
[40:35] multiple reddus instances. To put that
[40:38] far more clearly, Alice might be on
[40:40] Reddus instance one, but Bob's bucket
[40:42] might be on Reddus instance two. Okay?
[40:45] And so, let me demonstrate that here by
[40:49] adding a bunch of those. We need a
[40:52] million requests per second. And so, if
[40:54] we have 1 million divided by our 50K,
[40:57] well, this is 20. So, we'll need at
[40:59] least
[41:01] 20 of these. Maybe we want to tell the
[41:02] interviewer that we want a little bit of
[41:04] room for overhead, so we'd have more
[41:05] than that. But now the question becomes
[41:08] how do we shard? And this is important
[41:11] because the gateway always needs to know
[41:13] that I just got Alice's request. So I
[41:15] need to look in whichever Reddus
[41:17] instance has Alice's bucket. If we just
[41:20] checked a random bucket, then we might
[41:22] not have Alice. And if we just
[41:24] replicated all the data to each of these
[41:26] buckets, well, we're in the same
[41:28] problem, right? All of the buckets have
[41:30] all of the data. Um, and so we might run
[41:32] into issues of the actual amount of size
[41:36] that we're storing. These are in memory.
[41:38] So 64 GB, maybe go up to 10 and
[41:42] something gigabytes, right? But we can't
[41:44] store an infinite amount of data. So how
[41:46] do we want to shard? Well, you obviously
[41:48] want to shard based on whatever your
[41:50] client ID is. In this case, the user ID
[41:53] or the IP address or the API key. And
[41:56] you can use something like consistent
[41:58] hashing. I'll try to remember to put a
[42:00] link to our consistent hashing video
[42:02] somewhere on the screen now so you can
[42:03] click on it if you're not familiar with
[42:05] consistent hashing. Um, but in reality,
[42:08] what you'd probably end up doing if you
[42:10] are using Reddus is that you would use
[42:12] what's called Reddis cluster. And Reddis
[42:15] cluster manages this kind of sharding
[42:18] for you. Um, and it does this not
[42:21] actually using consistent hashing. It
[42:22] uses what's called hash slots. And so it
[42:25] has something like 60,000 hash slots
[42:27] that it distributes across each of these
[42:30] different Reddus nodes. It handles the
[42:32] distribution into which hash slot any
[42:34] given user is in and thus which Reddice
[42:36] node they're in. Um and then it will all
[42:39] be handled within what is called as I
[42:42] said reddis cluster and so that would be
[42:44] an easy way to handle this but the main
[42:47] conceptual thing for you to know into
[42:48] your in your interview is that we need
[42:49] multiple instances and thus we need to
[42:51] shard right easy enough.
[42:54] Um now the next thing that we should
[42:56] talk about then um again I'm going out
[42:58] of order is the availability over
[42:59] consistency and so how do we ensure that
[43:02] we have high availability and that we're
[43:04] also fault tolerant right and so if we
[43:08] come back here what happens if Reddus
[43:10] fails what happens if any of these
[43:12] particular instances fail if Alice's
[43:15] bucket is on this particular node and
[43:17] this node fails well then now Alice
[43:19] can't be rate limited okay and so the
[43:22] first thing that we might want to talk
[43:23] about is well what happens if that did
[43:25] happen and then we can talk about how we
[43:27] want to prevent it and so if that did
[43:30] happen then we have two options. Option
[43:32] one is fail open and option two is fail
[43:34] close. This is common terminology when
[43:36] you discuss rate limiters. Fail open
[43:39] means our rate limiter is down and thus
[43:41] every single request should get through.
[43:44] Fail close is the opposite. Our rate
[43:46] limiter is down and now no requests
[43:48] should get through. And so you'll
[43:50] probably want to talk to your
[43:51] interviewer in order to understand the
[43:52] requirements of this particular system.
[43:55] We've understood that we're designing a
[43:56] rate limiter for some sort of a social
[43:58] network. And so in the case of failing
[44:01] open, we would be kind of no longer
[44:05] protecting all of the services that we
[44:07] were here to protect. And it may
[44:09] introduce a bunch of issues downstream.
[44:11] Like there was a rate limiter here for a
[44:13] reason. And it's probably because there
[44:15] are limits to how many times we can read
[44:18] from our database or our cache or how
[44:20] many uh you know times we can compute
[44:24] something algorithmically within any of
[44:26] our microservices given the limitations
[44:28] that we have in CPU or even GPU
[44:30] respectively. Right? So in our case if
[44:32] we were to fail open we would basically
[44:33] say just go for it send all requests and
[44:36] then these microservices one by one
[44:38] might be back here and might die and go
[44:41] offline. we might have this cascading
[44:43] set of failures that are even worse. On
[44:45] the other hand, if we fail close, then
[44:46] now our site is down and you're going to
[44:49] have a bunch of users who are upset, who
[44:50] are reporting, oh no, Facebook,
[44:52] Instagram, whatever we're designing this
[44:54] rate limit for is down and that's maybe
[44:56] not good either. There's no right or
[44:58] wrong answer. I think typically what
[44:59] you're going to do here is you're going
[45:00] to fail close. The responsibility of the
[45:02] rate limiter is to protect the backend
[45:03] services to some degree. uh and thus if
[45:05] it's down then it needs to take what is
[45:08] the strictest um protection mechanism
[45:10] possible and that is to to reject
[45:12] everything. Um I will note that there's
[45:15] there's oftent times in real production
[45:17] systems more sophisticated things that
[45:19] you would do here than just this binary
[45:20] fail open or close like you can keep
[45:23] some state in the gateway. The the
[45:25] gateways themselves of course have
[45:26] memory and so maybe you have like a
[45:28] single counter in order to do a fixed
[45:30] window counter such that if these fell
[45:32] off then you could fall back to maybe
[45:34] the fixed window counter using the the
[45:36] memory um within the gateway and then it
[45:38] doesn't matter that we don't have the
[45:39] coordination between multiple gateway
[45:41] instances we talked before because it's
[45:42] like this is just a temporary thing
[45:44] while Reddis gets back up. It's better
[45:45] than nothing. It's better than failing
[45:47] open or failing close. At least we still
[45:49] have some rate limiting capacity. So if
[45:52] any of these go down, that's what we
[45:53] would do. But more importantly, how do
[45:54] we make sure that a I guess none of
[45:56] these go down and two that you know if
[45:58] they do go down, we get them up as as
[45:59] quickly as possible. And the key as is
[46:02] the case with most distributed systems
[46:04] is replicas,
[46:07] right? So we can we can configure a
[46:09] replication factor such that each one of
[46:12] our reddish shards each one of our nodes
[46:14] here have one or even two replicas such
[46:18] that all data that gets written to them
[46:20] also then gets propagated to its replica
[46:22] and if one of these were to go down
[46:25] then its replica would be promoted and
[46:27] all of the reads would then come to the
[46:30] replica instead.
[46:32] Now, similarly like we talked about with
[46:35] um with sharding, Reddis cluster
[46:38] actually supports this for you. And so
[46:40] with Reddis cluster, sorry about that
[46:42] noise in the background. There's some
[46:43] construction going on. I'll see if I can
[46:45] get that out in post. Um but similar to
[46:48] to to sharding with Reddis cluster, you
[46:50] can configure a number of these backups.
[46:52] And these backups use async replication.
[46:55] So it's not perfect. We're opting for
[46:57] high availability instead of
[46:59] consistency. That's the trade-off here.
[47:01] So a write happens um if this fails you
[47:06] know before the write gets written here
[47:08] asynchronously then yeah we'll be
[47:09] missing some data there but it's not the
[47:11] end of the world like now we think Alice
[47:13] is at 99 requests instead of 100 right
[47:16] she got one extra request off of us but
[47:18] no big deal so the key to uh the high
[47:21] availability and the fault tolerance is
[47:24] sharding and read replicas okay and
[47:28] reddis cluster can satisfy both of those
[47:30] now let's talk about the low latency
[47:32] rate limit checks. So how do we make
[47:33] sure that we're sub 10 millisecond
[47:35] latency? Well, every single check now is
[47:38] going to require this network round trip
[47:40] to Reddus and this is going to add
[47:41] latency to every single request of
[47:43] course and so Reddus operations are
[47:45] typically sub millisecond, but the
[47:48] network overhead here can be in some
[47:50] cases several milliseconds per request,
[47:53] right? And then the fact that we have
[47:55] you know these larger requests might
[47:57] make them even slightly longer. Um, and
[48:00] so the most important optimization that
[48:02] you can do right here is what's called
[48:03] connection pooling. And this is so
[48:05] instead of establishing a new TCP
[48:07] connection to Reddus for each rate limit
[48:09] check, your API gateway is going to
[48:11] maintain a pool of persistent
[48:12] connections here. And this is going to
[48:14] eliminate that TCP handshake overhead,
[48:17] which can sometimes be 20 to even 50
[48:19] milliseconds depending on your network
[48:20] distance. Okay. Um, and we're just going
[48:23] to reuse those same TCP connections.
[48:26] Now, this is interesting to say in your
[48:27] interview and you should talk to your
[48:28] interviewer about kind of TCP connection
[48:31] pooling, but note that most Reddus
[48:33] clients will handle connection pooling
[48:34] automatically for you. I don't know a
[48:36] single one that doesn't. It would be
[48:37] crazy if it doesn't. Um, but you may
[48:39] need to tune the pool size based on your
[48:42] request volume and the Reddus response
[48:43] time. So, this is a good thing to know.
[48:45] Um, but in your interviewer, you should
[48:47] probably tell your interviewer that you
[48:48] understand that you know this connection
[48:50] pooling will likely be be handled for
[48:52] you by whatever Reddus client you use.
[48:55] The other additional interesting thing
[48:56] to talk about here when it comes to
[48:57] latency is the geographic distribution.
[49:01] And so what you would want to do is you
[49:03] want to make sure that your rate limiter
[49:04] and even your gateway are as close to
[49:06] your users as possible. And so if you
[49:08] have users in Tokyo, then maybe you have
[49:10] a gateway that is somewhere in Asia or
[49:12] somewhere in Japan. And subsequently
[49:15] Reddus, your Reddus instance is located
[49:17] or colllocated with your gateway ideally
[49:19] even in the same data center as close as
[49:22] possible. Right? These two servers might
[49:23] even be right next to each other to try
[49:25] to minimize that latency as much as
[49:27] humanly possible. At this point, we
[49:29] should be feeling pretty good. We have
[49:30] satisfied all of our functional
[49:32] requirements. We've satisfied all of our
[49:33] non-functional requirements. But there's
[49:35] one more thing I want to talk to you all
[49:36] about that that's pretty common as it
[49:38] comes up in interviews. And I want to
[49:39] make sure that you guys are as well
[49:40] prepared as possible. And that's how do
[49:43] we handle dynamic rule configurations.
[49:46] And so right now we've just sort of
[49:48] assumed that there were static rules
[49:49] like maybe when the gateway was deployed
[49:51] it had some basic rules which said the
[49:53] token refill rate and you know the the
[49:58] the the token count in the bucket and so
[50:01] we always just use these rates these
[50:03] hard-coded rates and if you ever want to
[50:05] change it you would need to redeploy
[50:06] your gateway. Now you could also store
[50:09] them in Reddus. You could do a bunch of
[50:10] different things, but we've assumed thus
[50:12] far that they are static. And so what
[50:15] happens if they were configurable as is
[50:17] the case in most production systems? And
[50:19] sometimes you want to have different
[50:20] rules for different users and different
[50:22] types of things like we talked about
[50:23] with premium and otherwise. And so how
[50:25] would you handle that? Well, let's talk
[50:26] through a couple of options. The first
[50:29] maybe silly option would be that you
[50:31] your system has a database. This is a
[50:33] database, I'm sure, that your
[50:34] microservices are talking to. And it
[50:37] could store something like last, you
[50:40] know, whatever your rules are, which
[50:42] premium users, last refill or excuse me,
[50:46] refill rate, etc., right? And your
[50:49] gateway could maybe just periodically
[50:52] pull. And so maybe every 20 seconds it
[50:55] pulls like this. Okay, that's an option.
[50:58] Now, it's not an ideal option because a
[51:01] we have this 20 seconds delay here or 10
[51:04] seconds delay or even a 5-second delay
[51:06] and you could make it 1 second, but now
[51:08] you're just burning unnecessary gateway
[51:09] CPU that should be doing other things in
[51:11] order to do this constant pulling,
[51:13] right? So, that's not great. You can
[51:15] also of course just pull from Reddus
[51:17] like you definitely don't need the
[51:18] database in some of in each of these
[51:20] Reddus shards have that key value with
[51:24] all of the rules and periodically pull
[51:26] in the rules. Maybe even each time you
[51:29] check a rate limit request, check the
[51:31] actual rules, right? Look up the key
[51:33] that has the rules and find out if the
[51:34] rules have changed at all. This is just
[51:36] going to add additional operations to
[51:39] every single check and it's going to
[51:41] increase your latency unnecessarily
[51:43] considering rules probably aren't going
[51:44] to change that often. So it's an option
[51:48] but again probably not the best option.
[51:51] The best option is that you can use a
[51:53] pushbase configuration and actually
[51:56] zookeeper a bit outdated nowadays I must
[52:00] admit or etc.
[52:03] These are options here. The latter of
[52:05] which kind of being a bit more invogue
[52:06] than than the old school zookeeper, but
[52:09] I think conceptually the same general
[52:11] thing. And so what these are is that
[52:14] these are designed in order to maintain
[52:17] this distributed configuration
[52:19] management. And so the rules can be
[52:21] stored here. And not only can the
[52:24] gateway when it comes online ask for the
[52:26] rules and then store those rules
[52:29] importantly in memory. And it's going to
[52:31] keep those rules in memory. So it
[52:32] doesn't have to do a network check every
[52:33] time. It has those rules there. But it
[52:36] can also subscribe to watch for changes.
[52:40] And so what it can do is that then opens
[52:42] up a persistent TCP connection such that
[52:45] anytime a rule changes in Zookeeper that
[52:49] this gateway wants to know about, it
[52:50] gets pushed over that open TCP
[52:52] connection and then the gateway can
[52:54] update its rules in memory. And so this
[52:57] saves all of the issues with the or
[52:59] solves all of the issues with the
[53:00] previous two approaches which is that we
[53:02] don't have any additional latency or
[53:04] network requests because the rules are
[53:06] kept here and we don't have to pull.
[53:08] Zookeeper is just going to push. It's
[53:10] ready.
[53:13] There you have it folks. At this point
[53:15] we've satisfied our highle design and
[53:17] our deep dives and we have a pretty
[53:18] comprehensive design of a distributed
[53:21] rate limiter. Now, if you are a
[53:24] mid-level candidate, then the
[53:25] expectation is that you're going to have
[53:27] more 80% breadth and 20% depth. And so,
[53:30] I would expect from you as an uh as an
[53:32] interviewer, I would expect that you
[53:34] understand the different rate limiting
[53:36] algorithms and you make a choice and
[53:37] justify that choice appropriately. You
[53:39] might not be able to code them or know
[53:41] them perfectly in depth, but
[53:42] conceptually you should understand them.
[53:44] You should understand that the rate
[53:45] limiter would make the most sense
[53:46] existing on the edge of our system and
[53:48] you should propose something in order to
[53:51] share state globally whether that's
[53:53] reddis memcache or otherwise and be able
[53:55] to justify why you're adding it. Beyond
[53:58] there you should be able to answer my
[53:59] questions as I probe as an interviewer
[54:01] when I point out that there's
[54:02] limitations with a single reddus
[54:04] instance for example or when I ask
[54:06] questions about what happens when
[54:08] something goes down. You should be able
[54:10] to problem solve and arrive at
[54:12] reasonable answers given my probing and
[54:14] me leading you to the answers. Now for
[54:16] senior candidates on the hand I expect
[54:18] you to be much more proactive. You're
[54:20] identifying those issues proactively.
[54:21] You're telling me the interviewer that
[54:24] you recognize that a single reddest node
[54:25] isn't going to cut it here. Here's the
[54:27] math that proves why. And here's how
[54:29] many shards I'm going to need and what
[54:30] I'm going to shard on. Right? You're
[54:31] going to be more proactive in those
[54:32] ways. Talking to me about fault
[54:33] tolerance, but all the things that could
[54:35] potentially go wrong if the system gets
[54:37] overwhelmed. failing open, failing
[54:39] closed, etc. And then as a staff
[54:41] candidate, realistically this question
[54:42] is not asked nearly as often of staff
[54:44] candidates. Um, it's a little bit maybe
[54:47] kind of on the easier or medium side
[54:48] maybe. But if you are asked this as a
[54:50] staff candidate, I'm expecting a lot
[54:52] more depth. I'm expecting you to
[54:53] proactively lead through just about
[54:55] everything that we've talked about here
[54:56] maybe. U but then you'll also guide me
[54:58] towards conversations of things that you
[55:00] know really well. Maybe you have deep
[55:02] experience of Reddis cluster and you can
[55:04] tell me about times where you had to or
[55:06] you accidentally or incorrectly managed
[55:09] the connection pool size. Uh you made
[55:11] mistakes there and why it's important
[55:12] that it needs to be a particular size.
[55:14] Or you proactively recognize the race
[55:16] condition and you explain to me how
[55:18] Lewis scripting is going to work in
[55:19] order to solve the race condition.
[55:21] Right? That's a little bit more of an
[55:22] advanced concept. So uh that's how you
[55:24] would break it down. Mid-level um senior
[55:27] and staff respectively.
[55:30] Um, let's see. Anything else that I want
[55:32] to say here? I will put this diagram in
[55:34] the description. So, if you want it, go
[55:36] check it out there. I'll be posting more
[55:38] videos. Plenty more videos on this
[55:39] YouTube channel will be coming. And
[55:41] maybe the last thing, we're so close to
[55:42] 100,000 subscribers at time of recording
[55:44] this. If you liked it, please like,
[55:47] subscribe, leave a comment down below.
[55:49] I'll answer those. And uh, as always,
[55:52] best of luck with your upcoming
[55:54] interview. You guys are going to do
[55:55] great. Take care.
