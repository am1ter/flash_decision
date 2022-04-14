<template>
    <div id='app'>

        <div id='pagebackgroundtext'>
            <Background/>
        </div>

        <!-- Show error if there is any errors -->
        <div id='errors' v-if="apiErrors.length > 0">
            <div>{{apiErrors[0]}}</div>
            <b-button squared class="mt-3 gradient" v-on:click="reloadPage()">Refresh page</b-button>
        </div>

        <div id='header'>
            <Header/>
        </div>

        <div id='content' class="shadow">
            <Menu />
            <Title/>
            <router-view>
                <page_Login/>
                <page_Signup/>
                <page_Session/>
                <page_Decision/>
                <page_Results/>
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
    import page_Signup from './components/page_Signup.vue'
    import page_Session from './components/page_Session.vue'
    import page_Decision from './components/page_Decision.vue'
    import page_Results from './components/page_Results.vue'
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
            page_Signup,
            page_Session,
            page_Decision,
            page_Results,
            page_Scoreboard
        },
        computed: {
            ...mapState(['apiErrors'])
        },
        methods: {
            reloadPage() {
                // Reload page on click
                this.$router.push('/session/custom/')
                this.$router.go()
            }
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
        max-width: 453px;
        height: 100%;
        margin: auto;
    }

    #content {
        min-height: calc(100vh - 34px - 10px - 34px);
        max-width: 453px;
        margin: 0px auto;
        padding-bottom: 15px;
        background-color: #ffffff;
        opacity: 0.85;
    }

    #content_border_bottom {
        background: linear-gradient(to right, #271238, #113763, #0B5A73);
        height: 5px;
        max-width: 453px;
        width: 100%;
        margin: 0px auto;
    }

    #credits {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 35px;
        margin: 0px auto;
        max-width: 453px;
        width: 100%;
        text-align: center;
    }

    #page {
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        align-items: center;
        margin: 15px 25px;
        width: auto;
    }

    #errors {
        position: absolute;
        width: 100vw;
        height: 100vh;
        top: 0px;
        font-size: 24px;
        font-weight: 700;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        background-color: rgba(255,255,255,0.7);
        z-index: 1;
        text-align: center;
    }

    .disabled {
        opacity: 0.25;
        pointer-events: none;
    }

    .gradient {
        background: linear-gradient(to right, #271238, #113763, #0B5A73);
        color: #FFFFFF !important;
    }

    .gradient:focus, .gradient:hover {
        background: linear-gradient(to right, #280B3F, #0E4280, #076583);
        color: #FFFFFF !important;
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
        color: #000000 !important;
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

    .isInputInvalid {
        border: 1px solid #dc3545;
        border-radius: 3px;
        font-size: 14px;
        padding-right: calc(1.5em + .75rem)!important;
        background-image: url('./assets/icons/i_formvalidation_error.svg') !important;
        background-position: right calc(.375em + .1875rem) center;
        background-repeat: no-repeat;
        background-size: calc(.75em + .375rem) calc(.75em + .375rem);
    }

    .nav-link {
        color: #888888 !important;
        font-weight: 500;
        font-size: 16px;
        margin: 0px 10px;
        padding: 0px 5px !important;
        border-bottom: 1px solid #888888;
    }

    .nav-link.active {
        color: #0B5A73 !important;
        font-weight: 500;
        font-size: 16px;
        margin: 0px 10px;
        padding: 0px 5px !important;
        border-bottom: 1px solid #0B5A73;
    }

</style>
