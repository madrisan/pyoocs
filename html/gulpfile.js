var gulp        = require('gulp'),
    minifycss   = require('gulp-minify-css'),
    jshint      = require('gulp-jshint'),
    stylish     = require('jshint-stylish'),
    uglify      = require('gulp-uglify'),
    usemin      = require('gulp-usemin'),
    imagemin    = require('gulp-imagemin'),
    rename      = require('gulp-rename'),
    concat      = require('gulp-concat'),
    notify      = require('gulp-notify'),
    cache       = require('gulp-cache'),
    changed     = require('gulp-changed'),
    rev         = require('gulp-rev'),
    browserSync = require('browser-sync'),
    ngannotate  = require('gulp-ng-annotate'),
    del         = require('del'),
    less        = require('gulp-less');

var paths = {
    dist: 'json-server/public/'
};

gulp.task('jshint', function() {
    return gulp.src('app/scripts/**/*.js')
            .pipe(jshint())
            .pipe(jshint.reporter(stylish));
});

// Clean
gulp.task('clean', function() {
    return del([paths.dist]);
});

// Default task
gulp.task('default', ['clean'], function() {
    gulp.start('buildless', 'usemin', 'copyviews', 'imagemin', 'copyfonts');
});

gulp.task('usemin', ['buildless', 'jshint'], function () {
    return gulp.src('./app/index.html')
            .pipe(usemin({
                css:[minifycss(), rev()],
                js: [ngannotate(), uglify(), rev()]
            }))
            .pipe(gulp.dest(paths.dist));
});

// Views
gulp.task('copyviews', function() {
    return gulp.src('app/views/**/*.html')
            .pipe(gulp.dest(paths.dist + '/views/'));
});

// Images
gulp.task('imagemin', function() {
    return del([paths.dist + '/images/']), gulp.src('app/images/**/*')
            .pipe(cache(imagemin({
                optimizationLevel: 3,
                progressive: true,
                interlaced: true
            })))
            .pipe(gulp.dest(paths.dist + '/images/'))
            .pipe(notify({ message: 'Images task complete' }));
});

// Fonts
gulp.task('copyfonts', function() {
    gulp.src('./bower_components/font-awesome/fonts/**/*.{ttf,woff,eof,svg}*')
     .pipe(gulp.dest(paths.dist + '/fonts/'));

    gulp.src('./bower_components/bootstrap/dist/fonts/**/*.{ttf,woff,eof,svg}*')
     .pipe(gulp.dest(paths.dist + '/fonts/'));
});

// CSS
gulp.task('buildless', function() {
    return gulp.src('app/styles/**/*.less')
     .pipe(less())
     .pipe(gulp.dest('./app/styles'));
});

// Watch
gulp.task('watch', ['browser-sync'], function() {
  // Watch .js .css and .html files
  gulp.watch('{app/scripts/**/*.js,app/styles/**/*.less,app/**/*.html}', ['usemin']);

  // Watch views html files
  gulp.watch('app/views/**/*.html', ['copyviews']);

  // Watch image files
  gulp.watch('app/images/**/*', ['imagemin']);

});

gulp.task('browser-sync', ['default'], function () {
    var files = [
        'app/index.html',
        'app/views/**/*.html',
        'app/styles/**/*.css',
        'app/images/**/*.png',
        'app/scripts/**/*.js',
        paths.dist + '/**/*'
    ];

    browserSync.init(files, {
        server: {
            baseDir: paths.dist,
            index: "index.html"
        }
    });

    // Watch any files in dist/, reload on change
    gulp.watch([paths.dist + '/**']).on('change', browserSync.reload);
});
