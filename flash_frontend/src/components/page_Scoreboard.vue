<template>
    <section id='page' v-if="apiErrors.length == 0 & isLoaded">
        <div id='scoreboard_mode'>
            <!-- Navigation bar (modes) -->
            <ul class="nav justify-content-center">
                <li class="nav-item">
                    <a class="nav-link" 
                    :class="{active: isPageActive('custom')}"
                    role="button"
                    v-on:click="$router.push(`/scoreboard/custom/${user.id}`)">Custom</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" 
                    :class="{active: isPageActive('classic')}" 
                    role="button" 
                    v-on:click="$router.push(`/scoreboard/classic/${user.id}`)">Classic</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link"
                    :class="{active: isPageActive('blitz')}"
                    role="button"
                    v-on:click="$router.push(`/scoreboard/blitz/${user.id}`)">Blitz</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" 
                    :class="{active: isPageActive('crypto')}" 
                    role="button" 
                    v-on:click="$router.push(`/scoreboard/crypto/${user.id}`)">Crypto</a>
                </li>
            </ul>
            <!-- Empty scoreboard -->
            <div id='empty_scoreboard'
                v-if="Object.keys(top3Users).length == 0"
                class="text-center shadow col-12 mt-3 pt-3 pb-1">
                <h1>N/A</h1>
                <p>
                    Nobody has tried this mode yet<br>
                    Will you be the first one?
                </p>
            </div>
            <!-- Scoreboard data -->
            <!-- Top-3 users-->
            <b-container fluid v-for="(user, idx) in top3Users" :key="user.name">
                <!-- All users in top-3 except current user -->
                <b-row v-if="idx!=userRank" class="user_card" :class="{ user_card_champion: idx==0 }">
                    <b-col cols="2">
                        <img v-if="idx==0" src="../assets/icons/i_ava_champion.svg"/>
                        <img v-if="idx!=0" src="../assets/icons/i_ava_default.svg"/>
                    </b-col>
                    <b-col cols="6" class="user_card_col">
                        <p class="user_name">{{top3Users[idx]["name"]}} #{{parseInt(idx) + 1}}</p>
                        <p class="user_result">
                            Result: <span :class="formatFiguresColor(formatFigures(top3Users[idx]['result']))">{{top3Users[idx]["result"]}}%</span>
                        </p>
                    </b-col>
                    <b-col cols="4">
                        <p></p>
                    </b-col>
                </b-row>
                <!-- Display current user's summary if current user is in top-3) -->
                <b-row v-if="idx==userRank" class="user_card" :class="{ user_card_champion: idx==0 }">
                    <b-col cols="2">
                        <img v-if="idx==0" src="../assets/icons/i_ava_champion.svg"/>
                        <img v-if="idx!=0" src="../assets/icons/i_ava_default.svg"/>
                    </b-col>
                    <b-col cols="6" class="user_card_col">
                        <p class="user_name">{{userSummary.userName}} #{{userRank + 1}}</p>
                        <p class="user_result">
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
                    class="current_user_summary shadow"
                    :class="{ current_user_summary_champion: idx==0 }"
                />
            </b-container>
            <!-- Display current user's summary if current user is not in top-3 -->
            <b-container fluid v-if="userRank >= 3">
                ...
                <b-row class="user_card">
                    <b-col cols="2">
                        <img src="../assets/icons/i_ava_default.svg"/>
                    </b-col>
                    <b-col cols="6" class="user_card_col">
                        <p class="user_name">{{userSummary.userName}} #{{userRank + 1}}</p>
                        <p class="user_result">
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
                    class="current_user_summary shadow"
                />
            </b-container>
            <b-container fluid v-if="userRank == -1">
                ...
                <b-row class="user_card">
                    <b-col cols="2">
                        <img src="../assets/icons/i_ava_default.svg"/>
                    </b-col>
                    <b-col cols="10" class="user_card_col">
                        <p class="user_name">{{user.email}}</p>
                        <p class="user_result">
                            <a href="#" v-on:click="$router.push('/session/')">No results yes. Would you like to start start your first session?</a>
                        </p>
                    </b-col>
                </b-row>
            </b-container>
        </div>
    </section>
</template>

<script>
    import { mapState } from 'vuex'
    import { apiGetScoreboard } from '@/api'

    export default {
        name: 'page_Scoreboard',
        data() {
            return {
                isLoaded: false,
                mode: 'custom',
                top3Users: {},
                userRank: -1,
                userSummary: {},
                fields: [
                    { key: 'column' },
                    { key: 'value', tdClass: this.formatFiguresColor }
                ]
            }
        },
        computed: {
            ...mapState(['user', 'currentSession', 'apiErrors'])
        },
        mounted() {
            this.loadScoreboard()
        },
        beforeRouteUpdate(to, from, next) {
            // Send API request when mode nav bar used
            this.isLoaded = false
            this.mode = to.params.mode
            this.loadScoreboard()
            next()
        },
        methods: {
            async loadScoreboard() {
                // Load last session results
                let response = await apiGetScoreboard(this.mode, this.user.id)
                // Check if there is data for current user and current mode
                this.top3Users = (response) ? response.top3Users : false
                this.userRank = (response) ? response.userRank : -1
                this.userSummary = (response) ? response.userSummary : {}
                this.isLoaded = true
            },
            formatFigures(x) {
                // Improve text display of figures
                return (x > 0) ? '+' + x + '%': x + '%'
            },
            calcUserSummary() {
                // Format api user summary response to put it into bootstrap table
                let userSum = this.userSummary
                return [
                    { column: 'Total sessions', value: userSum.totalSessions},
                    { column: 'Profitable sessions', value: userSum.profitableSessions},
                    { column: 'Unprofitable sessions', value: userSum.unprofitableSessions},
                    { column: 'Total result', value: this.formatFigures(userSum.totalResult)},
                    { column: 'Median result', value: this.formatFigures(userSum.medianResult)},
                    { column: 'Best session result', value: this.formatFigures(userSum.bestSessionResult)},
                    { column: 'First session', value: userSum.firstSession}
                ]
            },
            formatFiguresColor(value) {
                // Change color of figures
                let firstChar = String(value).charAt(0)
                if(firstChar === '+')
                    return 'text-success'
                else if(firstChar === '-')
                    return 'text-danger'
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

    #scoreboard_mode {
        width: 100%;
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

    .user_card {
        border: 1px solid #888888;
        box-sizing: border-box;
        margin-top: 15px;
        padding: 10px 0px;
        box-shadow: 0px 4px 6px -4px rgba(24, 39, 75, 0.12), 0px 8px 8px -4px rgba(24, 39, 75, 0.08);
    }

    .user_card_champion {
        border: 2px solid #FFC107;
    }

    .user_card_col {
        display: flex;
        justify-content: center;
        flex-direction: column;
    }

    .user_name {
        font-weight: 500;
        font-size: 16px;
        margin-bottom: 0px;
    }

    .user_result {
        font-weight: 500;
        font-size: 12px;
        margin-bottom: 0px;
    }

    .current_user_summary {
        border-left: 1px solid #888888;
        border-right: 1px solid #888888;
        border-bottom: 1px solid #888888;
        box-sizing: border-box;
        box-shadow: 0px 4px 6px -4px rgba(24, 39, 75, 0.12), 0px 8px 8px -4px rgba(24, 39, 75, 0.08);
        font-size: 14px;
    }
    
    .current_user_summary_champion {
        border-left: 1px solid #FFC107;
        border-right: 1px solid #FFC107;
        border-bottom: 1px solid #FFC107;
    }

    .container-fluid {
        padding: 0px;
    }

    .row {
        margin-left: 0px;
        margin-right: 0px;
    }

</style>
