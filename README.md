## Jenerator: Julia sets generator 

### How to use

Julia sets are sets of points (in this case in the complex plane) that border non-diverging and diverging points.  This means that a point is in a Julia set if it sits next to one that heads towards infinity over time, and also next to another that does not.  Even with very simple equations, the resulting Julia sets can be spectacular.

To use this app, follow the link provided in the 'About' section on this page.  After a short wait (as the free servers sleep when not in use), the following page will appear:

![screenshot](/assets/Screenshot_jenerator.png)

There are three primary input fields: `Real value`, `Imaginary value`, and `Maximum iterations`.  The first two fields specify the equation shown to the right of the `CLICK TO RUN` button, and the coordinates chosen by the user are displayed by the red X symbol on the Mandelbrot set to the left of the inputs.  

Choosing values that place the red X inside the dark central region of the Mandelbrot set leads to a globular Julia set, whereas placing the X outside the Mandelbrot set leads to disconnected 'dusts'. In general, the Julia set is most visually interesting when the values chosen place the red X near the (lighter in color) border region of the Mandelbrot set.

The `Maximum iterations` field tells the program how many iterations of the equation displayed should be performed.  Increasing this value will often give better map clarity, at the expense of longer computation time.  Likewise, the 'Resolution' field will increase resolution at the expense of time, as more calculations are required for a given area.

For z² + -0.764 + 0.12i, the following image is produced:

![image](/assets/julia.png)


## Behind the scenes

The Jenerator is a flask app using a Dash interface for front end and callbacks.  Computation is handed off to a Redis server via a Redis Queue message broker, and the Redis server is pinged every two seconds by the app to see if computation is complete.  The actual computation is performed using Numpy, and the resulting array is transformed into an image via matplotlib and saved to a temporary memory buffer as a bytestring using a base64 binary encoding.  When the Redis job is complete, it is fetched and the bytestring is decoded into a PNG that can be opened in a separate page for maximum resolution.  

This system of background Redis processes circumvents the problem of long computation times faced at higher resolutions.  Heroku (and most other cloud PaaS) have hard time limits (30s in this case) and so simply having the server compute an array for longer than this results in a timeout error.  Timeouts do not occur even when computations run for more than 5 minutes with the current configuration because the app is continually 'active' as it pings the Redis server.  

The generation of a Julia set only occurs when the `CLICK TO RUN` button is pressed, but real-time callbacks for placing the red X on the correct position in the Mandelbrot set and displaying the correct equation occur upon any modification of the real or imaginary values.  These processes do not employ redis (as they are very fast) but are performed directly in the flask app using helper functions.  The callback graph is as follows:

![image](/assets/jenerator_graph.png)

## Learn more

To learn more about Julia sets and the mathematical ideas behind them, see the following page on [Julia sets](https://blbadger.github.io/julia-sets.html) or [this page](https://blbadger.github.io/mandelbrot-set.html) on the Mandelbrot set.  If you like the Jenerator, you may also like the [Pfinder](https://github.com/blbadger/pfinder) too.

