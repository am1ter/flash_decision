<template>
    <section id='page' v-if="isLoaded">
        <div id='errors' v-if="apiErrors.length > 0">
            <p>{{apiErrors[0]}}</p>
        </div>
        <b-table outlined striped no-border-collapse hover :items="calcSessionsSummary" :fields="fields" thead-class="d-none" class="shadow">
        </b-table>
        <b-button type="submit" class="col-12 gradient rounded-1" href="/#/scoreboard">Go to the leaderboard</b-button>
    </section>
</template>

<script>
    import { mapState } from 'vuex'
    import { getSessionsResults } from '@/api'

    export default {
        name: 'page_Results',
        data() {
            return {
                isLoaded: false,
                apiErrors: [],
                fields: [
                    { key: 'column' },
                    { key: 'value', tdClass: 'setValueTdClass' }
                ]
            }
        },
        computed: {
            ...mapState(['isAuth', 'user', 'currentSession'])
        },
        async mounted() {
            await this.loadSessionsResults()
        },
        methods: {
            loadSessionsResults() {
                // Load last session results
                getSessionsResults(this.currentSession.options.sessionId)
                    .then(response => {
                        this.currentSession['sessionsResults'] = response.data
                        this.isLoaded = true
                    },
                    reject => {this.apiErrors.push(reject)}
                    )
            },
            formatFigures(x) {
                return (x > 0) ? '+' + x + '%': x + '%'
            },
            calcSessionsSummary() {
                console.log('Table shown')
                let sesRes = this.currentSession.sessionsResults
                return [
                    { column: 'Total result', value: this.formatFigures(sesRes.totalResult)},
                    { column: 'Total decisions', value: sesRes.totalDecisions},
                    { column: 'Profitable decisions', value: sesRes.profitableDecisions},
                    { column: 'Unprofitable decisions', value: sesRes.unprofitableDecisions},
                    { column: 'Skipped decisions', value: sesRes.skippedDecisions},
                    { column: 'Median decision’s result', value: this.formatFigures(sesRes.medianDecisionsResult)},
                    { column: 'Best decision’s result', value: this.formatFigures(sesRes.bestDecisionsResult)},
                    { column: 'Worst decision’s result', value: this.formatFigures(sesRes.worstDecisionsResult)},
                    { column: 'Total time spent', value: sesRes.totalTimeSpent},
                ]
            },
            setValueTdClass(value) {
                var firstChar = String(value).charAt(0)
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

</style>
