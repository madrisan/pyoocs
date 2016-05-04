var gulp        = require('gulp'),
    cleancss    = require('gulp-clean-css'),
    jshint      = require('gulp-jshint'),
    stylish     = require('jshint-stylish'),
    uglify      = require('gulp-uglify'),
    usemin      = require('gulp-usemin'),
    imagemin    = require('gulp-imagemin'),
    rename      = require('gulp-rename'),
    concat      = require('gulp-concat'),
    cache       = require('gulp-cache'),
    changed     = require('gulp-changed'),
    rev         = require('gulp-rev'),
    browserSync = require('browser-sync'),
    ngannotate  = require('gulp-ng-annotate'),
    del         = require('del'),
    less        = require('gulp-less');

var cfg = {
    dist: 'public/'
};

// JavaScript syntax checker
gulp.task('jshint', function() {
    return gulp.src('client/app/scripts/**/*.js')
            .pipe(jshint())
            .pipe(jshint.reporter(stylish));
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
    gulp.start('buildless', 'usemin', 'copyviews', 'imagemin', 'copyfonts');
});

// Minification and uglification
gulp.task('usemin', ['buildless', 'jshint'], function () {
    return gulp.src('client/app/index.html')
            .pipe(usemin({
                css: [cleancss({compatibility: 'ie8'}), rev()],
                js: [ngannotate(), /*uglify(),*/ rev()]
            }))
            .pipe(gulp.dest(cfg.dist));
});

// Views
gulp.task('copyviews', function() {
    return gulp.src('client/app/views/**/*.html')
            .pipe(gulp.dest(cfg.dist + '/views/'));
});

// Images
gulp.task('imagemin', function() {
    return del([cfg.dist + '/images/']), gulp.src('client/app/images/favicon.ico')
            //.pipe(cache(imagemin({
            //    optimizationLevel: 3,
            //    progressive: true,
            //    interlaced: true
            //})))
            .pipe(gulp.dest(cfg.dist + '/images/'));
});

// Fonts
gulp.task('copyfonts', function() {
    gulp.src('client/bower_components/font-awesome/fonts/**/*.{ttf,woff,eof,svg}*')
     .pipe(gulp.dest(cfg.dist + '/fonts/'));

    gulp.src('client/bower_components/bootstrap/dist/fonts/**/*.{ttf,woff,eof,svg}*')
     .pipe(gulp.dest(cfg.dist + '/fonts/'));
});

// CSS
gulp.task('buildless', function() {
    return gulp.src('client/app/styles/**/*.less')
     .pipe(less())
     .pipe(gulp.dest('client/app/styles'));
});

// Watch
gulp.task('watch', ['browser-sync'], function() {
  // Watch .js .css and .html files
  gulp.watch('{client/app/scripts/**/*.js,client/app/styles/**/*.less,client/app/**/*.html}', ['usemin']);

  // Watch views html files
  gulp.watch('client/app/views/**/*.html', ['copyviews']);

  // Watch image files
  gulp.watch('client/app/images/**/*', ['imagemin']);
});

gulp.task('browser-sync', ['default'], function () {
    var files = [
        'client/app/index.html',
        'client/app/views/**/*.html',
        'client/app/styles/**/*.css',
        'client/app/images/**/*.png',
        'client/app/scripts/**/*.js',
        cfg.dist + '/**/*'
    ];

    browserSync.init(files, {
        server: {
            baseDir: cfg.dist,
            index: "index.html"
        }
    });

    // Watch any files in dist/, reload on change
    gulp.watch([cfg.dist + '/**']).on('change', browserSync.reload);
});
