# ── Add these routes to your main.py ──────────────────────────────────────────
# Also add at top of main.py:
# from booking import check_availability, book_slot, BookSlotRequest, CheckAvailabilityRequest

@app.post("/check-availability")
def check_availability_endpoint(request: CheckAvailabilityRequest):
    """
    Check available interview slots for a given date.
    Used by ElevenLabs tool to show available times to caller.
    """
    try:
        slots = check_availability(request.date, request.timezone)
        if not slots:
            return {
                "available": False,
                "message": f"No available slots on {request.date}. Please try another date.",
                "slots": []
            }
        # Return max 5 slots to keep voice response concise
        return {
            "available": True,
            "date": request.date,
            "slots": slots[:5],
            "message": f"Available slots on {request.date}: " + ", ".join(
                [s[11:16] for s in slots[:5]]  # Extract HH:MM from ISO string
            )
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/book-slot")
def book_slot_endpoint(request: BookSlotRequest):
    """
    Book an interview slot on Cal.com.
    Called by ElevenLabs tool after caller confirms a time.
    """
    try:
        booking = book_slot(
            name=request.name,
            email=request.email,
            start_time=request.start_time,
            timezone=request.timezone,
            notes=request.notes
        )
        return {
            "success": True,
            "message": f"Interview booked successfully for {request.name}! "
                      f"A confirmation has been sent to {request.email}. "
                      f"Booking ID: {booking['booking_id']}",
            "booking": booking
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))