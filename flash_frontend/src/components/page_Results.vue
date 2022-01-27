<template>
    <section id='page'>
        <div id='errors' v-if="apiErrors.length > 0">
            <p>{{apiErrors[0]}}</p>
        </div>
        <div class="text-center">You have earned <b>{{ currentSession.sessionResult }}%</b> during this session</div>
    </section>
</template>

<script>
    import { mapState } from 'vuex'
    import { getScoreboard } from '@/api'

    export default {
        name: 'page_Results',
        data() {
            return {
                apiErrors: []
            }
        },
        computed: {
            ...mapState(['isAuth', 'user', 'currentSession'])
        },
        mounted() {
            this.loadScoreboard()
        },
        methods: {
            loadScoreboard() {
                // Load last session results
                getScoreboard(this.user.id, this.currentSession.options.sessionId)
                    .then(response => {
                        this.currentSession['sessionResult'] = Math.round(response.data * 100 * 10**5) / 10**5
                    },
                    reject => {this.apiErrors.push(reject)}
                    )
            }
        }
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
