<script>
  import { Link, Router, Route } from "svelte-routing";

  import home from "./routes/home.svelte";
  import interview from "./routes/interview.svelte";
  import journeymap from "./routes/journeymap.svelte";
  import about from "./routes/about.svelte";

  export let url = "";
</script>

<Router {url}>
  <nav>
    <Link class="link" to="/">Home</Link>
    <Link class="link" to="interview">Interview</Link>
    <Link class="link" to="journeymap">Journey Map</Link>
    <!-- <Link to="about">About</Link> -->
  </nav>
  <main>
    <Route path="/interview" component={interview} />
    <Route path="/journeymap" component={journeymap} />
    <!-- <Route path="/about" component={about} /> -->
    <Route path="/" component={home} />
  </main>
</Router>

<style>
  nav {
    height: 50px;
  }
  .link {
    margin: 0 5px;
  }
  main {
    flex: 1;
  }
</style>
