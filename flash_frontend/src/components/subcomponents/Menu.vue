<template>
    <section id="menu" :class="{ disabled: !isAuth }">
            <router-link
            id="button-menu-session" tag="div" class="menu-button" 
            :to="`/session/`"
            :class="{ 'menu-active': checkPageIsActive('session') }">
                <img v-if="checkPageIsActive('session')" src="@/assets/icons/i_menu_session_active.svg" alt="Icon">
                <img v-else src="@/assets/icons/i_menu_session_inactive.svg" alt="Icon">
                <p class="menu-text">Session</p>
            </router-link>
            <router-link 
            id="button-menu-decision" tag="div" class="menu-button"
            :to="makeUrlForDecisionButton()"
            :class="{ 'menu-active': checkPageIsActive('decision'), 'disabled': checkNoSession()}">
                <img v-if="checkPageIsActive('decision')" src="@/assets/icons/i_menu_decision_active.svg" alt="Icon">
                <img v-else src="@/assets/icons/i_menu_decision_inactive.svg" alt="Icon">
                <p class="menu-text" >Decision</p>
            </router-link>
            <router-link
            id="button-menu-scoreboard" tag="div" class="menu-button"
            :to="`/scoreboard/custom/${insUrlParamUserId()}/`"
            :class="{ 'menu-active': checkPageIsActive('scoreboard') }">
                <img v-if="checkPageIsActive('scoreboard')" src="@/assets/icons/i_menu_scoreboard_active.svg" alt="Icon">
                <img v-else src="@/assets/icons/i_menu_scoreboard_inactive.svg" alt="Icon">
                <p class="menu-text">Scoreboard</p>
            </router-link>
    </section>
</template>

<script>
    import { mapState } from "vuex"
    export default {
        name: "Menu",
        props: {},
        computed: {
            ...mapState(["user", "currentSession"]),
            isAuth() {
                return this.$store.getters.isAuth
            }
        },
        methods: {
            checkPageIsActive(menu_element) {
                // Change styles for menu elements
                // Required as decision's tab used for 2 pages (decisions and session results)
                let menu_paths = {
                    "session": ["session"],
                    "decision": ["decision", "sessions-results"],
                    "scoreboard": ["scoreboard"]
                }
                let current_page = this.$route.path.split("/")[1]
                return menu_paths[menu_element].indexOf(current_page) >= 0
            },
            checkNoSession() {
                // Apply class 'disabled' if session hasn't started yet
                let noSession = (this.currentSession["currentIterationNum"] == undefined) && (isNaN(parseInt(this.$route.params.iteration_num)))
                return noSession
            },
            insUrlParamSessionId() {
                // Used for return to the session's results page
                // Check if session has been started and there is sessionId
                let sessionId = (Object.keys(this.currentSession["options"]["values"]).length != 0) ? this.currentSession["options"]["values"]["sessionId"] : 0
                return sessionId
            },
            insUrlParamUserId() {
                // Used for return to the session's results page
                // Check if session has been started and there is sessionId
                let link_postfix = ("id" in this.user) ? this.user.id : 0
                return link_postfix
            },
            makeUrlForDecisionButton() {
                // Make url for decision button: go to decisions or go to session results
                let url = ''
                let isSessionStarted = this.currentSession["currentIterationNum"] != undefined
                let isSessionFinished = Object.keys(this.currentSession["sessionsResults"]).length > 0

                if (isSessionFinished) {
                    url = `/sessions-results/${this.insUrlParamSessionId()}/`
                } else if (isSessionStarted) {
                    url = `/decision/${this.insUrlParamSessionId()}/${this.currentSession["currentIterationNum"]}`
                }

                return url
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
        border-bottom: 1px solid #076583;
        box-shadow: 0px -2px 8px 4px rgba(24, 39, 75, 0.05);
    }

    .menu-button {
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

    .menu-button:hover {
        background-color: #ffffff;
        border-bottom: 1px solid #271238;
        margin-bottom: -1px;
    }

    .menu-active {
        background-color: #0B5A73;
        color: #ffffff;
        border-bottom: 1px solid #333333;
        margin-bottom: -1px;
    }   

    .menu-active:hover {
        background-color: #0c4e63 !important;
    }

    .menu-text {
        margin: 15px 0px 15px 5px;
        font-weight: 500;
    }


</style>
