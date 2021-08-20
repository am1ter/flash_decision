<template>
    <div id='app'>

        <div id='pagebackgroundtext'>
            <Background/>
        </div>

        <div id='header'>
            <Header/>
        </div>

        <div id='content' class="shadow">
            <Menu class="shadow-sm"/>
            <Title/>
            <router-view>
                <page_Login/>
                <page_Session/>
                <page_Decision/>
                <page_Scoreboard/>
            </router-view>
        </div>

        <div id='content_border_bottom'/>

        <div id='credits'>
            <Credits/>
        </div>

    </div>
</template>

<script>
    import { mapState } from 'vuex'

    // Service components
    import Background from './components/Background.vue'
    import Header from './components/Header.vue'
    import Menu from './components/Menu.vue'
    import Title from './components/Title.vue'
    import Credits from './components/Credits.vue'
    
    // Pages components
    import page_Login from './components/page_Login.vue'
    import page_Session from './components/page_Session.vue'
    import page_Decision from './components/page_Decision.vue'
    import page_Scoreboard from './components/page_Scoreboard.vue'

    export default {
        name: 'App',
        components: {
            Background,
            Header,
            Menu,
            Title,
            Credits,
            page_Login,
            page_Session,
            page_Decision,
            page_Scoreboard
        },
        computed: {
            ...mapState(['sessions', 'isAuth'])
        },
        beforeMount() {
            // this.$store.dispatch('loadSessions')
        }
    }

</script>

<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap');

    body {
        font-family: 'Roboto', sans-serif;
        font-weight: 400;
        font-size: 16px;
        color: #333333;
        background-color: #ffffff;
        overflow: hidden;
        height: 100%;
        width: 100%;
        margin: 0; 
    }

    a {
        color: #333333 !important;
        text-decoration-line: none !important;
    }

    a:hover {
        color: #271238 !important;
    }

    .form-control {
        font-size: 16px;
    }

    #header {
        width: 453px;
        height: 100%;
        margin: 15px auto 10px auto;
    }

    #content {
        min-height: 85vh;
        width: 453px;
        margin: 0px auto;
        padding-bottom: 15px;
        background-color: #ffffff;
        opacity: 0.85;
    }

    #content_border_bottom {
        height: 5px;
        width: 453px;
        background: linear-gradient(to right, #271238, #113763, #0B5A73);
        margin: 0px auto 10px auto;
    }

    #credits {
        height: auto;
        width: 453px;
        margin: 0px auto 0px auto;
        text-align: center;
    }

    .disabled {
        opacity: 25%;
        pointer-events: none;
    }

    .gradient {
        background: linear-gradient(to right, #271238, #113763, #0B5A73);
    }

    .gradient:focus, .gradient:hover {
        background: linear-gradient(to right, #280B3F, #0E4280, #076583);
    }

    *:focus {
        outline: none;
    }
   
    .dropdown {
    /* Override custom Vue dropdown plugin style */
        border: 1px solid #ced4da;
        border-radius: 3px;
    }
    
    .dropdown:hover, .dropdown:focus, .dropdown:active {
    /* Override custom Vue dropdown plugin style */
        min-width: 100% !important;
        max-width: 100% !important;
        border: 1px solid #076583;
        border-radius: 3px;
    }

    .dropdown-input {
    /* Override custom Vue dropdown plugin style */
        min-width: 100% !important;
        max-width: 100% !important;
        font-size: 14px !important;
        color: #6c757d !important;
    }

    .dropdown-content, .dropdown-item {
    /* Override custom Vue dropdown plugin style */
        min-width: calc(100% + 2px) !important;
        max-width: calc(100% + 2px) !important;
        font-size: 16px !important;
        left: -1px;
        margin-top: 1px;
        margin-right: -1px;
        overflow-x: hidden !important;
        font-size: 14px !important;
    }

</style>
