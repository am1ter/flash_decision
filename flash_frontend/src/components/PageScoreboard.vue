<template>
    <section id="page" v-if="!isLoading">
        <div id="scoreboard-mode">

            <!-- Navigation bar (modes) -->
            <ModeSelector :page="'scoreboard'" :userId="user.id"/>

            <!-- Empty scoreboard -->
            <div id="scoreboard-empty"
                v-if="Object.keys(top3Users).length == 0"
                class="text-center shadow col-12 mt-3 pt-3 pb-1">
                <h1>N/A</h1>
                <p>
                    Nobody has tried this mode yet.<br>
                    Will you be the first one?
                </p>
            </div>

            <!-- Scoreboard data -->
            <!-- Top-3 users-->
            <b-container fluid v-for="(user, idx) in top3Users" :key="user.name">
                <!-- All users in top-3 except current user -->
                <b-row v-if="idx!=userRank" class="usercard" :class="{ 'usercard-champion': idx==0 }">
                    <b-col cols="2">
                        <img v-if="idx==0" src="../assets/icons/i_ava_champion.svg"/>
                        <img v-if="idx!=0" src="../assets/icons/i_ava_default.svg"/>
                    </b-col>
                    <b-col cols="6" class="usercard-col">
                        <p class="user_name">{{top3Users[idx]["name"]}} #{{parseInt(idx) + 1}}</p>
                        <p class="user-result">
                            Result: <span :class="formatFiguresColor(formatFigures(top3Users[idx]['result']))">{{top3Users[idx]["result"]}}%</span>
                        </p>
                    </b-col>
                    <b-col cols="4">
                        <p></p>
                    </b-col>
                </b-row>

                <!-- Display current user`s summary if current user is in top-3 -->
                <b-row v-if="idx==userRank" class="usercard" :class="{ 'usercard-champion': idx==0, 'usercard-current-user': userRank > 0 }">
                    <b-col cols="2">
                        <img v-if="idx==0" src="../assets/icons/i_ava_champion.svg"/>
                        <img v-if="idx!=0" src="../assets/icons/i_ava_default.svg"/>
                    </b-col>
                    <b-col cols="6" class="usercard-col">
                        <p class="user_name">{{userSummary.userName}} #{{userRank + 1}}</p>
                        <p class="user-result">
                            Result: <span :class="formatFiguresColor(formatFigures(userSummary.totalResult))">{{userSummary.totalResult}}%</span>
                        </p>
                    </b-col>
                    <b-col cols="4">
                        <p></p>
                    </b-col>
                </b-row>
                <b-table  
                    v-if="idx==userRank"
                    striped borderless hover thead-class="d-none"
                    :items="calcUserSummary"
                    :fields="fields"
                    class="current-user-summary shadow"
                    :class="{ 'current-user-summary-champion': idx==0 }"
                />
            </b-container>

            <!-- Display current user`s summary if current user is not in top-3 -->
            <b-container fluid v-if="userRank >= 3">
                ...
                <b-row class="usercard usercard-current-user">
                    <b-col cols="2">
                        <img src="../assets/icons/i_ava_default.svg"/>
                    </b-col>
                    <b-col cols="6" class="usercard-col">
                        <p class="user_name">{{userSummary.userName}} #{{userRank + 1}}</p>
                        <p class="user-result">
                            Result: <span :class="formatFiguresColor(formatFigures(userSummary.totalResult))">{{userSummary.totalResult}}%</span>
                        </p>
                    </b-col>
                    <b-col cols="4">
                        <p></p>
                    </b-col>
                </b-row>
                <b-table  
                    striped borderless hover thead-class="d-none"
                    :items="calcUserSummary"
                    :fields="fields"
                    class="current-user-summary shadow"
                />
            </b-container>
            <!-- Display card for case when user has no results for specified mode -->
            <b-container fluid v-if="userRank == -1 & Object.keys(top3Users).length != 0">
                ...
                <b-row class="usercard">
                    <b-col cols="2">
                        <img src="../assets/icons/i_ava_default.svg"/>
                    </b-col>
                    <b-col cols="10" class="usercard-col">
                        <p class="user_name">{{user.email}}</p>
                        <p class="user-result">
                            <a href="#" v-on:click="$router.push('/session/')">No results yes. Would you like to start start your first session?</a>
                        </p>
                    </b-col>
                </b-row>
            </b-container>
        </div>
    </section>
</template>

<script>
    import { mapState, mapMutations } from "vuex"
    import { apiGetScoreboard } from "@/api"

    // Pages subcomponents
    import ModeSelector from "./subcomponents/ModeSelector.vue"

    export default {
        name: "PageScoreboard",
        components: {
            ModeSelector
        },
        data() {
            return {
                mode: this.$route.params.mode,
                top3Users: {},
                userRank: -1,
                userSummary: {},
                fields: [
                    { key: "column" },
                    { key: "value", tdClass: this.formatFiguresColor }
                ]
            }
        },
        computed: {
            ...mapState(["user", "currentSession", "isLoading"])
        },
        async beforeMount() {
            // Start page loading
            this.startLoading()
            // Load scoreboard for current mode
            this.mode = this.$route.params.mode
            await this.loadScoreboard()
            // Display page
            this.stopLoading()
        },
        // Send API request when mode nav bar used
        async beforeRouteUpdate(to, from, next) {
            // Start page loading after route updating
            this.startLoading()
            // Load scoreboard for current mode
            this.mode = to.params.mode
            await this.loadScoreboard()
            await next()
            // Display page
            this.stopLoading()
        },
        methods: {
            ...mapMutations(["startLoading", "stopLoading"]),
            async loadScoreboard() {
                // Load last session results
                let response = await apiGetScoreboard(this.mode, this.user.id)
                // Check if there is data for current user and current mode
                this.top3Users = (response) ? response.top3Users : false
                this.userRank = (response) ? response.userRank : -1
                this.userSummary = (response) ? response.userSummary : {}
            },
            formatFigures(x) {
                // Improve text display of figures
                return (x > 0) ? "+" + x + "%": x + "%"
            },
            calcUserSummary() {
                // Format api user summary response to put it into bootstrap table
                let userSum = this.userSummary
                return [
                    { column: "Total sessions", value: userSum.totalSessions},
                    { column: "Profitable sessions", value: userSum.profitableSessions},
                    { column: "Unprofitable sessions", value: userSum.unprofitableSessions},
                    { column: "Total result", value: this.formatFigures(userSum.totalResult)},
                    { column: "Median result", value: this.formatFigures(userSum.medianResult)},
                    { column: "Best session result", value: this.formatFigures(userSum.bestSessionResult)},
                    { column: "First session", value: userSum.firstSession}
                ]
            },
            formatFiguresColor(value) {
                // Change color of figures
                let firstChar = String(value).charAt(0)
                if(firstChar === "+")
                    return "text-success"
                else if(firstChar === "-")
                    return "text-danger"
            },
            isPageActive(nav_item) {
                // Check if navbar item is active
                return this.$route.params.mode == nav_item
            }
        }
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

    #scoreboard-mode {
        width: 100%;
    }

    .usercard {
        border: 1px solid #888888;
        box-sizing: border-box;
        margin-top: 15px;
        padding: 10px 0px;
        box-shadow: 0px 4px 6px -4px rgba(24, 39, 75, 0.12), 0px 8px 8px -4px rgba(24, 39, 75, 0.08);
    }

    .usercard-champion {
        border: 2px solid #FFC107;
    }

    .usercard-current-user {
        border: 1px solid #076583 !important;
    }

    .usercard-col {
        display: flex;
        justify-content: center;
        flex-direction: column;
    }

    .user_name {
        font-weight: 500;
        font-size: 16px;
        margin-bottom: 0px;
    }

    .user-result {
        font-weight: 500;
        font-size: 12px;
        margin-bottom: 0px;
    }

    .current-user-summary {
        border-left: 1px solid #076583;
        border-right: 1px solid #076583;
        border-bottom: 1px solid #076583;
        box-shadow: 0px 4px 6px -4px rgba(24, 39, 75, 0.12), 0px 8px 8px -4px rgba(24, 39, 75, 0.08);
        font-size: 14px;
    }
    
    .current-user-summary-champion {
        border-left: 1.5px solid #FFC107;
        border-right: 1.5px solid #FFC107;
        border-bottom: 1.5px solid #FFC107;
    }

    .container-fluid {
        padding: 0px;
    }

    .row {
        margin-left: 0px;
        margin-right: 0px;
    }

</style>
