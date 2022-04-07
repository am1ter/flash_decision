<template>
    <section id='page'>
        <div id='empty_scoreboard'
            v-if="apiErrors.length == 0 & isLoaded & Object.keys(top3Users).length == 0" class="text-center shadow col-12 pt-2">
            <h1>N/A</h1>
            <p>
                Nobody has tried this mode yet<br>
                Will you be the first one?
            </p>
        </div>
        <div v-if="isLoaded" id='scoreboard_mode'>
                <b-tabs pills align="center" active-nav-item-class="text-light">
                    <b-tab title="Custom" class="mt-3" active>
                        <!-- Top-3 users-->
                        <b-container fluid v-for="(user, idx) in top3Users" :key="user.name">
                            <!-- All users in top-3 except current user -->
                            <b-row v-if="idx!=userRank" class="user_card" :class="{ user_card_champion: idx==0 }">
                                <b-col sm="2">
                                    <img v-if="idx==0" src="../assets/icons/i_ava_champion.svg"/>
                                    <img v-if="idx!=0" src="../assets/icons/i_ava_default.svg"/>
                                </b-col>
                                <b-col sm="6" class="user_card_col">
                                    <p class="user_name">{{top3Users[idx]["name"]}} #{{parseInt(idx) + 1}}</p>
                                    <p class="user_result">Result: <span class="text-success">{{top3Users[idx]["result"]}}%</span></p>
                                </b-col>
                                <b-col sm="4">
                                    <p></p>
                                </b-col>
                            </b-row>
                            <!-- Display current user's summary if current user is in top-3) -->
                            <b-row v-if="idx==userRank" class="user_card" :class="{ user_card_champion: idx==0 }">
                                <b-col sm="2">
                                    <img v-if="idx==0" src="../assets/icons/i_ava_champion.svg"/>
                                    <img v-if="idx!=0" src="../assets/icons/i_ava_default.svg"/>
                                </b-col>
                                <b-col sm="6" class="user_card_col">
                                    <p class="user_name">{{userSummary.userName}} #{{userRank + 1}}</p>
                                    <p class="user_result">Result: <span class="text-success">{{userSummary.totalResult}}%</span></p>
                                </b-col>
                                <b-col sm="4">
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
                        <b-container fluid v-if="userRank >= 4">
                            ...
                            <b-row class="user_card">
                                <b-col sm="2">
                                    <img src="../assets/icons/i_ava_default.svg"/>
                                </b-col>
                                <b-col sm="6" class="user_card_col">
                                    <p class="user_name">{{userSummary.userName}} #{{userRank + 1}}</p>
                                    <p class="user_result">Result: <span class="text-success">{{userSummary.totalResult}}%</span></p>
                                </b-col>
                                <b-col sm="4">
                                    <p></p>
                                </b-col>
                            </b-row>
                            <b-table  
                                v-if="idx==userRank"
                                striped borderless hover thead-class="d-none"
                                :items="calcUserSummary"
                                :fields="fields"
                                class="current_user_summary shadow"
                            />
                        </b-container>
                    </b-tab>
                    <b-tab title="Classic" class="mt-3">
                        <b-card-text>TBD</b-card-text>
                    </b-tab>
                    <b-tab title="Blitz" class="mt-3">
                        <b-card-text>TBD</b-card-text>
                    </b-tab>
                </b-tabs>
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
                top3Users: {},
                userRank: {},
                userSummary: {},
                fields: [
                    { key: 'column' },
                    { key: 'value', tdClass: this.setValueTdClass }
                ]
            }
        },
        computed: {
            ...mapState(['user', 'currentSession', 'apiErrors'])
        },
        mounted() {
            this.loadScoreboard()
        },
        methods: {
            async loadScoreboard() {
                // Load last session results
                let mode = 'custom'
                let response = await apiGetScoreboard(mode, this.user.id)
                console.log(response)
                this.top3Users = response.top3Users
                this.userRank = response.userRank
                this.userSummary = response.userSummary
                this.isLoaded = true
            },
            formatFigures(x) {
                // Improve text display of figures
                return (x > 0) ? '+' + x + '%': x + '%'
            },
            calcUserSummary() {
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
            setValueTdClass(value) {
                let firstChar = String(value).charAt(0)
                console.log(firstChar)
                if(firstChar === '+')
                    return 'text-success'
                else if(firstChar === '-')
                    return 'text-danger'
            }
        }
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    #scoreboard_mode {
        width: 100%;
    }

    .font_white {
        color: white;
    }

    .user_card {
        border: 2px solid #888888;
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
        border-left: 2px solid #888888;
        border-right: 2px solid #888888;
        border-bottom: 2px solid #888888;
        box-sizing: border-box;
        box-shadow: 0px 4px 6px -4px rgba(24, 39, 75, 0.12), 0px 8px 8px -4px rgba(24, 39, 75, 0.08);
        font-size: 14px;
    }
    
    .current_user_summary_champion {
        border-left: 2px solid #FFC107;
        border-right: 2px solid #FFC107;
        border-bottom: 2px solid #FFC107;
    }

    .container-fluid {
        padding: 0px;
    }

    .row {
        margin-left: 0px;
        margin-right: 0px;
    }

</style>
