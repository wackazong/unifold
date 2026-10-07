---
name: notifier-add-a-message
description: Add or change the text of a notification in the notifier library. Use it when a quantity or bound has no text of its own yet, or when a text shall be reworded.
---
# Add or change a notification text

The result is a text for one combination of quantity and bound, in the
table of texts and in the code. Alerts without a text of their own get
the general text, so this procedure can run before or after such alerts
exist.

## Steps

1. **Find the row.** Open the table "Texts" in
   [notification](../../references/notification.md). For a new quantity
   add two rows, one for `min` and one for `max`.
2. **Write the body.** First the state of the plant in two or three
   words, then the measured fact with value, unit and threshold. Use the
   unit and the number of decimals of the quantity
   ([context](../../context.md)).
3. **Check the length.** Fill in the longest possible numbers. The body
   has at most 120 characters.
4. **Check that nothing varies.** The body depends only on fields of the
   alert. No time of sending, no count
   ([0001](../../decisions/0001-once-means-repeatable-with-a-collapse-identifier.md)).
5. **Have a human read the text.** Wording is a product matter.
6. **Change the code and its test** so that both match the table.

## Checks

- For each new row: a call with that quantity and bound produces exactly
  the body of the table with the numbers filled in.
- Two calls with the same alert produce equal requests.
- An unknown quantity still produces "Needs attention."
- No body exceeds 120 characters at the ends of the range of its
  quantity.

## Reference

- [notification](../../references/notification.md): the texts and the
  request
- [context](../../context.md): units and resolutions of the quantities
