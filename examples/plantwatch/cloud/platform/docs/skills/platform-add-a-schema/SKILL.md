---
name: platform-add-a-schema
description: Give a service its own schema and role in the shared database. Use it when a service that stores data is added.
---
# Add a schema for a service

The result is an empty schema and a role that can use this schema and no
other. The service fills the schema itself.

## Steps

1. **Get the request.** You need the name of the service. Schema and role
   both get this name, with `-` replaced by `_`.
2. **Check that the service has none yet.** One service has one schema. A
   service that wants a second one probably wants to be two services.
3. **Declare the role** in the role declarations of this unit, with a
   connection limit of 20 and no right to create roles, databases or
   schemas.
4. **Declare the schema** with the role as its owner. Set the search path
   of the role to the schema.
5. **Remove default access.** Make sure the role has no rights on the
   schema `public` and on no other service's schema, and that no other
   service role has rights on the new schema.
6. **Create the secret.** Generate a password for the role and store it in
   the deployment's secret store under the service's name. Do not write it
   into a file of the repository.
7. **Deploy** `platform` to the test environment and check (below), then
   to production.

## Checks

- Connected as the new role: creating a table in the own schema works.
- Connected as the new role: reading a table of another schema fails with
  a permission error. Listing the tables of another schema shows nothing.
- Connected as another service's role: the new schema is not visible.
- The backup of the following night contains the new schema.

## Reference

- [SQL database](../../references/sql-db.md): what a role may do, limits
- [context](../../explanation/context.md): the rule that each service owns its data
