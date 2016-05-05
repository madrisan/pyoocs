function setupAuth(User, app) {
    var passport = require('passport')
      , localStrategy = require('passport-local').Strategy;

    //var secret = require('./config/secure')

    // Express middlewares
    // see: https://github.com/expressjs/session#options
    //app.use(require('express-session')({
    //    secret: secret.session_cookie,
    //    resave: false,
    //    saveUninitialized: false
    //}));

    // Passport middleware
    app.use(passport.initialize());
    app.use(passport.session());

    // Configure the local strategy for use by Passport.
    passport.use(new localStrategy(User.authenticate()));

    // Configure Passport authenticated session persistence.
    //passport.serializeUser(function(user, done) {
    //    done(null, user._id);
    //});
    passport.serializeUser(User.serializeUser());

    //passport.deserializeUser(function(id, done) {
    //    User.findOne({ _id : id }, function(error, user) {
    //        done(error, user);
    //    });
    //});
    passport.deserializeUser(User.deserializeUser());
};

module.exports = setupAuth;
