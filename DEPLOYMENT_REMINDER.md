# VPS Deployment Reminder

## When to Pull & Test on VPS

After completing each main phase, you should:

1. **Push to GitHub** - Complete the phase, then:
   ```bash
   git add .
   git commit -m "Phase X.Y complete"
   git push
   ```

2. **Pull in Portainer** - On your VPS:
   - Go to your Stack
   - Update the image pull policy to "Always" 
   - Or manually pull: `docker-compose -f docker-compose.companion.yml pull`

3. **Redeploy** - Recreate containers to get the latest code

4. **Test** - Verify the new features work on the live VPS

---

## Quick Test Commands (VPS)
```bash
# Check containers are running
docker-compose -f docker-compose.companion.yml ps

# View logs
docker-compose -f docker-compose.companion.yml logs -f
```