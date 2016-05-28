function setupAuth(User, app) {
    var passport = require('passport')
      , localStrategy = require('passport-local').Strategy;

    // Configure passport middleware
    app.use(passport.initialize());
    app.use(passport.session());

    // Configure the local strategy for use by Passport.
    passport.use(new localStrategy({
            usernameField: 'email',
            passwordField: 'password'
        },
        function verify(email, password, done) {
            //console.log('email: ' + email);
            //console.log('password: ' + password);
            User.findOne(
                { "profile.email": email },
                function(error, user) {
                    if (error) { return done(err); }

                    //console.log('user :' + user.profile.email);
                    if (!user) { return done(null, false); }
                    if (user.profile.password != password) {
                        return done(null, false);
                    }
                    // invoke 'done' with a user object, which will be set at 'req.user'
                    // in route handlers after authentication
                    return done(null, user);
                });
        }
    ));

    // Configure Passport authenticated session persistence.
    passport.serializeUser(function(user, done) {
        //console.log('passport.serializeUser: user: ' + user);
        //console.log('passport.serializeUser: user._id: ' + user._id);
        done(null, user._id);
    });
    passport.deserializeUser(function(id, done) {
        User.findOne({ _id : id }, function(error, user) {
            done(error, user);
        });
    });
};

module.exports = setupAuth;
