<template>
    <div id='app'>

        <div id='pagebackgroundtext'>
            <Background/>
        </div>

        <div id='header'>
            <Header username='amiter'/>
        </div>

        <div id='content'>
            <Menu :page='page'/>
            <Title :page='page'/>
            <router-view>
                <Session/>
                <Decision/>
                <Scoreboard/>
            </router-view>
        </div>

        <div id='credits'>
            <Credits version='0.4.02'/>
        </div>

    </div>
</template>

<script>
    // Service components
    import Background from './components/Background.vue'
    import Header from './components/Header.vue'
    import Menu from './components/Menu.vue'
    import Title from './components/Title.vue'
    import Credits from './components/Credits.vue'
    
    // Pages components
    import Session from './components/Session.vue'
    import Decision from './components/Decision.vue'
    import Scoreboard from './components/Scoreboard.vue'

    export default {
        name: 'App',
        components: {
            Background,
            Header,
            Menu,
            Title,
            Session,
            Decision,
            Scoreboard,
            Credits
        },
        computed: {
            page() {
                return this.$route.path
            },
            page_name() {
                return this.$route.name
            }
        }
    }

</script>

<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap');

    body {
        font-family: 'Roboto', sans-serif;
        font-weight: 400;
        font-size: 14px;
        color: #333333;
        background-color: #ffffff;
        overflow: hidden;
        height: 100%;
        width: 100%;
        margin: 0; 
    }

    a {
        color: #333333;
        text-decoration-line: none;
    }

    #pagebackgroundtext {
        font-size: 288px;
        color: #000000;
        opacity: 0.05;
        z-index: -1;
        position: absolute;
        display: block;
        width: 100%;
        top: -20%;
        text-align: center;
    }

    #header {
        width: 453px;
        height: 100%;
        margin: 15px auto 15px auto;
    }

    #content {
        height: 500px;
        width: 453px;
        margin: 0px auto 15px auto;
        background-color: #E5E5E5;
        opacity: 0.8;
    }

    #credits {
        height: auto;
        width: 453px;
        margin: 0px auto 0px auto;
        text-align: center;
    }

    .text_no_margin {
        margin: 0px;
    }

</style>
