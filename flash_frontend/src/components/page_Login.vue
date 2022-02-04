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
        <b-button href="/#/sign-up" variant="outline-secondary" class="col-12 my-2">Sign up</b-button>
    </section>
</template>

<script>
    export default {
        name: 'page_Login'
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
