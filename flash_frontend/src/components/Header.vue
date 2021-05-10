<template>
    <div id="app">

        <section class="header">
            <div class="header_container_left">
              <router-link to="/start" class="menu">Start</router-link>
              <router-link to="/terminal" class="menu">Terminal</router-link>
              <router-link to="/scoreboard" class="menu">Scoreboard</router-link>
            </div>
          <div class="header_container_right">
              <a class="menu" href="#">Login</a>
            </div>
        </section>

    </div>
</template>

<script>

</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

    .header {
        display: flex;
        /*height: 40px;*/
        margin: -8px;
        padding: 8px;

        background: #464646;
    }

    .header_container_left {
        flex: 50%;
        text-align: left;
    }

    .header_container_right {
        flex: 50%;
        text-align: right;
    }

    .menu {
        font-family: Roboto;
        color: #ffffff;
        margin: 0px 20px;
    }

</style>
