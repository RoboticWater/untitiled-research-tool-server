<script>
  import { Link, Router, Route } from "svelte-routing";

  import home from "./routes/home.svelte";
  import interview from "./routes/interview.svelte";
  import about from "./routes/about.svelte";

  export let url = "";
</script>

<Router {url}>
  <nav>
    <Link to="/">Home</Link>
    <Link to="interview">Interview</Link>
    <Link to="about">About</Link>
  </nav>
  <main>
      <Route path="/interview" component={interview} />
      <Route path="/about" component={about} />
      <Route path="/" component={home} />
  </main>
</Router>

<style>
  nav {
    height: 50px;
  }
</style>