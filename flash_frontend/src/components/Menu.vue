<template>
    <section id='menu' :class='{ disabled: !isAuth }'>
            <router-link to='/session' tag="div" class='menu_button' :class='{ "menu-active": checkPageIsActive("session") }'>
                <img v-if='checkPageIsActive("session")' src='../assets/icons/i_menu_session_active.svg' alt='Icon'>
                <img v-else src='../assets/icons/i_menu_session_inactive.svg' alt='Icon'>
                <p class='menu_text'>Session</p>
            </router-link>
            <router-link :to="{name: 'Session’s results page', params: {'session_id': insUrlParamSessionId()}}" tag="div" class='menu_button' :class='{ "menu-active": checkPageIsActive("decision"), "disabled": checkIsSessionBlank()}'>
                <img v-if='checkPageIsActive("decision")' src='../assets/icons/i_menu_decision_active.svg' alt='Icon'>
                <img v-else src='../assets/icons/i_menu_decision_inactive.svg' alt='Icon'>
                <p class='menu_text' >Decision</p>
            </router-link>
            <router-link :to="{name: 'Scoreboard page', params: {'mode': 'custom', 'user_id': insUrlParamUserId()}}" tag="div" class='menu_button' :class='{ "menu-active": checkPageIsActive("scoreboard") }'>
                <img v-if='checkPageIsActive("scoreboard")' src='../assets/icons/i_menu_scoreboard_active.svg' alt='Icon'>
                <img v-else src='../assets/icons/i_menu_scoreboard_inactive.svg' alt='Icon'>
                <p class='menu_text'>Scoreboard</p>
            </router-link>
    </section>
</template>

<script>
    import { mapState } from 'vuex'
    export default {
        name: 'Menu',
        props: {},
        computed: {
            ...mapState(['user', 'currentSession']),
            isAuth() {
                return this.$store.getters.isAuth
            }
        },
        methods: {
            checkPageIsActive(menu_element) {
                // Change styles for menu elements
                // Required as decision's tab used for 2 pages (decisions and session results)
                let menu_paths = {
                    'session': ['session'],
                    'decision': ['decision', 'sessions-results'],
                    'scoreboard': ['scoreboard']
                }
                let current_page = this.$route.path.split('/')[1]
                return menu_paths[menu_element].indexOf(current_page) >= 0
            },
            checkIsSessionBlank() {
                // Apply class 'disabled' if session hasn't started yet
                if (this.isAuth) {
                    let ses_started = !('options' in this.currentSession)
                    return ses_started
                } else {
                    return false
                }
            },
            insUrlParamSessionId() {
                // Used for return to the session's results page
                // Check if session has been started and there is sessionId
                let link_postfix = ('options' in this.currentSession) ? this.currentSession.options.sessionId : 0
                return link_postfix
            },
            insUrlParamUserId() {
                // Used for return to the session's results page
                // Check if session has been started and there is sessionId
                let link_postfix = ('id' in this.user) ? this.user.id : 0
                return link_postfix
            }
        }
    }
</script>

<!-- Add 'scoped' attribute to limit CSS to this component only -->
<style scoped>

    #menu {
        background: #E5E5E5;
        width: 100%;
        text-align: center;
        display: flex;
        flex-direction: row;
        align-items: center;
        border-bottom: 1px solid #0B5A73;
    }

    .menu_button {
        flex: 1;
        width: 100%;
        height: 100%;
        font-family: Roboto;
        color: #333333;
        display: flex;
        justify-content: center;
        align-items: center;
        cursor: pointer;
    }

    .menu_button:hover {
        box-shadow: 0px -1px 0px #271238 inset;
    }

    .menu_button.router-link-active:hover {
        background-color: #0c4e63;
    }

    .menu_button:hover:not(.router-link-active) {
        background-color: #ffffff;
    }


    .menu_text {
        margin: 15px 5px;
        font-weight: 500;
    }

    .router-link-active {
        background-color: #0B5A73;
        color: #ffffff;
        box-shadow: 0px -1px 0px #333333 inset;
    }
    
    .menu-active {
        background-color: #0B5A73;
        color: #ffffff;
        box-shadow: 0px -1px 0px #333333 inset;
    }   

    .menu-active:hover {
        background-color: #0c4e63 !important;
    }

</style>
