var gulp        = require('gulp')
  , browserSync = require('browser-sync')
  , cache       = require('gulp-cache')
  , changed     = require('gulp-changed')
  , cleancss    = require('gulp-clean-css')
  , concat      = require('gulp-concat')
  , del         = require('del')
  , imagemin    = require('gulp-imagemin')
  , jshint      = require('gulp-jshint')
  , less        = require('gulp-less')
  , mocha       = require('gulp-mocha')
  , ngannotate  = require('gulp-ng-annotate')
  , rename      = require('gulp-rename')
  , rev         = require('gulp-rev')
  , stylish     = require('jshint-stylish')
  , uglify      = require('gulp-uglify')
  , usemin      = require('gulp-usemin');

var cfg = {
    dist: 'public/'
};

// JavaScript syntax checker
gulp.task('jshint', function() {
    return gulp.
        src('client/app/js/**/*.js').
        pipe(jshint()).
        pipe(jshint.reporter(stylish));
});

// Clean
gulp.task('clean', function() {
    return del([cfg.dist]);
});

// Clear cache
gulp.task('clearcache', function (done) {
    return cache.clearAll(done);
});

// Default task
gulp.task('default', ['clean'], function() {
    gulp.start('buildless',
               'usemin',
               'copyviews',
               'imagemin',
               'copyfonts');
});

// Minification and uglification
gulp.task('usemin', ['buildless', 'jshint'], function () {
    return gulp.
        src('client/app/index.html').
        pipe(usemin({
            css: [cleancss({compatibility: 'ie8'}), rev()],
            js: [ngannotate(), /*uglify(),*/ rev()]
        })).
        pipe(gulp.dest(cfg.dist));
});

// Views
gulp.task('copyviews', function() {
    return gulp.
        src('client/app/views/**/*.html').
        pipe(gulp.dest(cfg.dist + '/views/'));
});

// Images
gulp.task('imagemin', function() {
    return del([cfg.dist + '/img/']), gulp.
        src('client/app/img/**/*.{ico,jpg}').
    //  pipe(cache(imagemin({
    //      optimizationLevel: 3,
    //      progressive: true,
    //      interlaced: true
    //  }))).
        pipe(gulp.dest(cfg.dist + '/img/'));
});

// Fonts
gulp.task('copyfonts', function() {
    gulp.
        src('client/bower_components/font-awesome/fonts/**/*.{ttf,woff,eof,svg}*').
        pipe(gulp.dest(cfg.dist + '/fonts/'));

    gulp.
        src('client/bower_components/bootstrap/dist/fonts/**/*.{ttf,woff,eof,svg}*').
        pipe(gulp.dest(cfg.dist + '/fonts/'));
});

// CSS
gulp.task('buildless', function() {
    return gulp.
        src('client/app/css/**/*.less').
        pipe(less()).
        pipe(gulp.dest('client/app/css'));
});

// Watch
gulp.task('watch', ['browser-sync'], function() {
    // Watch .js .css and .html files
    gulp.watch('{ client/app/js/**/*.js,  \
                  client/app/css/**/*.less, \
                  client/app/**/*.html }', ['usemin']);

    // Watch views html files
    gulp.watch('client/app/views/**/*.html', ['copyviews']);

    // Watch image files
    gulp.watch('client/app/img/**/*', ['imagemin']);
});

// Test
gulp.task('test', ['usemin', 'copyviews', 'imagemin', 'copyfonts'], function() {
    var error = false;
    gulp.
        src('./test.js').
        pipe(mocha()).
        on('error', function() {
            console.log('Tests failed!');
            error = true;
        }).
        on('end', function() {
            if (!error) {
                console.log('Tests succeeded!');
                process.exit(0);
            }
        });
});


gulp.task('browser-sync', ['default'], function () {
    var files = [
        'client/app/index.html',
        'client/app/views/**/*.html',
        'client/app/css/**/*.css',
        'client/app/img/**/*.png',
        'client/app/js/**/*.js',
        './test.js',
        cfg.dist + '/**/*'
    ];

    browserSync.init(files, {
        port: 8080,
        server: {
            baseDir: cfg.dist,
            index: "index.html"
        }
    });

    // Watch any files in dist/, reload on change
    gulp.
        watch([cfg.dist + '/**']).
        on('change', browserSync.reload);
});
