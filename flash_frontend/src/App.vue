<template>
    <div id="app">

        <Loading :active.sync="isLoading" :canCancel=false :loader="'dots'" :color="'#076583'"/>
        <Error/>

        <div id="background-text">
            <Background/>
        </div>

        <div id="content" class="shadow" :class="{disabled: apiErrors.length > 0}">
             <Header/>
            <router-view>
                <PageLogin/>
                <PageSignup/>
                <PageSession/>
                <PageSessionForm/>
                <PageDecision/>
                <PageResults/>
                <PageScoreboard/>
            </router-view>
        </div>

        <div id="content-border-bottom"/>

        <div id="credits">
            <Credits/>
        </div>

    </div>
</template>

<script>
    import { mapState } from "vuex"

    // Service components
    import Background from "./components/Background.vue"
    import Header from "./components/Header.vue"
    import Credits from "./components/Credits.vue"
    import Error from "./components/Error.vue"
    
    // Pages components
    import PageLogin from "./components/PageLogin.vue"
    import PageSignup from "./components/PageSignup.vue"
    import PageSession from "./components/PageSession.vue"
    import PageSessionForm from "./components/PageSessionForm.vue"
    import PageDecision from "./components/PageDecision.vue"
    import PageResults from "./components/PageResults.vue"
    import PageScoreboard from "./components/PageScoreboard.vue"

    export default {
        name: "App",
        components: {
            Error,
            Background,
            Header,
            Credits,
            PageLogin,
            PageSignup,
            PageSession,
            PageSessionForm,
            PageDecision,
            PageResults,
            PageScoreboard
        },
        computed: {
            ...mapState(["apiErrors", "isLoading"])
        }
    }

</script>

<style>
    @import url("https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap");

    body {
        font-family: "Roboto", sans-serif;
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

    #content {
        min-height: calc(100vh - 89px - 25px - 20px);
        max-width: 453px;
        margin: 0px auto;
        padding-bottom: 5px;
        background-color: #ffffff;
        opacity: 0.85;
    }

    #content-border-bottom {
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
        margin: 15px 25px 5px 25px;
        width: auto;
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

    .is-input-invalid {
        border: 1px solid #dc3545 !important;
        border-radius: 3px;
        font-size: 14px;
        padding-right: calc(1.5em + .75rem)!important;
        background-image: url("./assets/icons/i_formvalidation_error.svg") !important;
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
