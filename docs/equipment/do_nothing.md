[Table of contents](../readme.md)
# Do_Nothing

The do_nothing instrument, invoked by `type = do_nothing`, is a dummy instrument that intercepts all method calls the class and returns None if the method is a setter and 1 if it's a getter.

For specific methods an override can be implemented, e.g. to return a tuple.
