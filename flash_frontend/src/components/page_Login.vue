<template>
    <section id='page'>
        <b-container class="g-0 text-center" fluid>
            <b-row cols="2">
                <b-col class="my-auto" sm="3"><label>Email</label></b-col>
                <b-col class="my-auto" sm="9"><b-form-input id="input-email" placeholder="Enter your email"/></b-col>
                <div class="w-100 my-1"></div>
                <b-col class="my-auto" sm="3"><label>Password</label></b-col>
                <b-col class="my-auto" sm="9"><b-form-input type='password' id="input-password" placeholder="Enter your password"/></b-col>
            </b-row>
        </b-container>
        <b-button class="col-12 mt-3 gradient">Sign in</b-button>
        <b-button v-on:click="goToSignUp()" variant="outline-secondary" class="col-12 my-2">Sign up</b-button>
        <b-button v-on:click="useDemoAccount()" variant="outline-secondary" class="col-12">Sign in with demo account</b-button>
    </section>
</template>

<script>
    import { mapState, mapMutations } from 'vuex'

    export default {
        name: 'page_Login',
        computed: {
            ...mapState(['isAuth', 'user', 'registrationForm', 'apiErrors'])
        },
        methods: {
            ...mapMutations(['setAuth', 'setUser']),
            goToSignUp() {
                // Go to the sign up page
                this.$router.push('/sign-up/')
            },
            useDemoAccount() {
                let user = {'id': 1, 'email': 'demo@alekseisemenov.ru'}
                this.$store.commit('setUser', user)
                this.$store.commit('setAuth', true)
                // Go to the main page
                this.$router.push('/session/')
            }
        }
    }
</script>

<style scoped>
    #page {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin: 15px 25px;
        width: auto;
    }
</style>
