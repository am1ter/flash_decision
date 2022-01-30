<template>
    <section id='page'>
        <div id='errors' v-if="apiErrors.length > 0">
            <p>{{apiErrors[0]}}</p>
        </div>
        <div v-if="apiErrors == 0 & isLoaded" class="text-center shadow col-12 pt-2">
            <h1>N/A</h1>
            <p>
                Nobody has tried this mode yet<br>
                Will you be the first one?
            </p>
        </div>
    </section>
</template>

<script>
    import { mapState } from 'vuex'
    import { getScoreboard } from '@/api'

    export default {
        name: 'page_Scoreboard',
        data() {
            return {
                isLoaded: false,
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
                getScoreboard(this.user.id)
                    .then(response => {
                        console.log(response)
                        this.isLoaded = true
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
