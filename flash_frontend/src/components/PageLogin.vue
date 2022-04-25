<template>
    <section id="page" v-if="apiErrors.length == 0 & isLoaded">
        <form @submit.prevent="checkForm">
            <b-container class="g-0" fluid>
                <b-row cols="2">
                    <b-col class="my-auto text-center col-3"><label>Email</label></b-col>
                    <b-col class="my-auto col-9"><b-form-input id="input-email" placeholder="Enter your email"/></b-col>
                    <div class="w-100 my-1"></div>
                    <b-col class="my-auto text-center col-3"><label>Password</label></b-col>
                    <b-col class="my-auto col-9"><b-form-input type="password" id="input-password" placeholder="Enter your password"/></b-col>
                    <div class="w-100 my-1"></div>
                    <b-col class="my-auto col-3" v-if="formErrors.indexOf('input-password') > -1">
                        <!-- Empty cell -->
                    </b-col>
                    <b-col class="my-auto col-9" v-if="formErrors.indexOf('input-password') > -1">
                        <p class="text-danger text-left mb-0">
                            <small>Incorrect email or password</small>
                        </p>
                    </b-col>
                </b-row>
            </b-container>
            <b-button id="button-signin" type="submit" squared class="col-12 mt-3 gradient">Sign in</b-button>
            <b-button id="button-signup" v-on:click="goToSignUp()" squared variant="outline-secondary" class="col-12 my-2">Sign up</b-button>
            <b-button id="button-signin-demo" v-on:click="useDemoAccount()" squared variant="outline-secondary" class="col-12">Sign in with demo account</b-button>
        </form>
    </section>
</template>

<script>
    import { mapState, mapMutations } from "vuex"
    import { apiPostLogin } from "@/api"

    export default {
        name: "PageLogin",
        data() {
            return {
                isLoaded: true,
                formErrors: []
                }
        },
        computed: {
            ...mapState(["user", "apiErrors"])
        },
        methods: {
            ...mapMutations(["setUserFromApi"]),
            goToSignUp() {
                // Go to the sign up page
                this.$router.push("/sign-up/")
            },
            async useDemoAccount() {
                let creds = {"email": "demo@alekseisemenov.ru", "password": "demo"}
                let user = await apiPostLogin(creds)
                if (user) {
                    this.$store.commit("setUserFromApi", user)
                    // Go to the main page
                    this.$router.push("/session/")
                } else {
                    this.formErrors.push("input-password")
                }
            },
            async checkForm() {
                // Get data from inputs and send it via API
                let input_login = this.$children[0].localValue
                let input_password = this.$children[1].localValue            
                let form = {"email": input_login, "password": input_password}

                // Stop if blank login or password
                if (!input_login || !input_password) {
                    return false
                }

                // Check form via api (authenticated or not)
                let user = await apiPostLogin(form)
                if (user) {
                    this.$store.commit("setUserFromApi", user)
                    // Go to the main page
                    this.$router.push("/session/")
                } else {
                    this.formErrors.push("input-password")
                }
            }
        }
    }
</script>

<style scoped>

    #page {
        height: calc(100vh - 54px - 113px - 34px - 80px);
    }

</style>
